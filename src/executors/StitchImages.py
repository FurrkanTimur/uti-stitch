import os
import cv2
import sys
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

from sdks.novavision.src.media.image import Image
from sdks.novavision.src.base.component import Component
from sdks.novavision.src.helper.executor import Executor
from components.Stitch.src.utils.response_stitch_images import build_response_stitch_images
from components.Stitch.src.models.PackageModel import PackageModel


class StitchImages(Component):
    def __init__(self, request, bootstrap):
        super().__init__(request, bootstrap)
        self.request.model = PackageModel(**(self.request.data))
        self.imageA = self.request.get_param("inputImageA")
        self.imageB = self.request.get_param("inputImageB")
        self.knn_k = self.request.get_param("configCountOfBestMatchesPerQueryDescriptor")
        self.reproj_error = self.request.get_param("configMaxAllowedReprojectionError")

    @staticmethod
    def bootstrap(config: dict) -> dict:
        return {}

    def stitch_images(self, image1, image2, count_of_best_matches_per_query_descriptor, max_allowed_reprojection_error):
        sift = cv2.SIFT_create()

        keypoints_1, descriptors_1 = sift.detectAndCompute(image=image1, mask=None)
        keypoints_2, descriptors_2 = sift.detectAndCompute(image=image2, mask=None)
        print(f"[StitchImages DEBUG] kp1={len(keypoints_1)} kp2={len(keypoints_2)}", flush=True)

        bf = cv2.BFMatcher_create()
        matches = bf.knnMatch(
            queryDescriptors=descriptors_1,
            trainDescriptors=descriptors_2,
            k=count_of_best_matches_per_query_descriptor,
        )

        good_matches = [m[0] for m in matches if m[0].distance < 0.75 * m[1].distance]
        print(f"[StitchImages DEBUG] total_matches={len(matches)} good_matches={len(good_matches)} "
              f"ransac_thresh={max_allowed_reprojection_error}", flush=True)

        image1_pts = np.float32([keypoints_1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        image2_pts = np.float32([keypoints_2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        image1_first = np.mean([kp.pt[0] for kp in keypoints_1]) < np.mean([kp.pt[0] for kp in keypoints_2])
        if image1_first:
            first_image_pts = image1_pts
            second_image_pts = image2_pts
            first_image = image2
            second_image = image1
        else:
            first_image_pts = image2_pts
            second_image_pts = image1_pts
            first_image = image1
            second_image = image2

        transformation_matrix, mask = cv2.findHomography(
            srcPoints=first_image_pts,
            dstPoints=second_image_pts,
            method=cv2.RANSAC,
            ransacReprojThreshold=max_allowed_reprojection_error,
        )
        inliers = int(mask.sum()) if mask is not None else 0
        print(f"[StitchImages DEBUG] inliers={inliers}/{len(good_matches)}", flush=True)

        h1, w1 = first_image.shape[:2]
        h2, w2 = second_image.shape[:2]

        warped_image_corners = cv2.perspectiveTransform(
            src=np.float32([[0, 0], [0, h2], [w2, h2], [w2, 0]]).reshape(-1, 1, 2),
            m=transformation_matrix,
        )
        [xmin, ymin] = np.int32(warped_image_corners.min(axis=0).ravel())
        [xmax, ymax] = np.int32(warped_image_corners.max(axis=0).ravel())

        # first_image always sits at the canvas origin (0, 0) with size (w1, h1);
        # the canvas bounds must include its corners too, or the width/height
        # computed below can end up smaller than what warpPerspective actually
        # needs once translation_dist is clamped to non-negative, clipping part
        # of the warped second_image out of the output.
        xmin = min(xmin, 0)
        ymin = min(ymin, 0)
        xmax = max(xmax, w1)
        ymax = max(ymax, h1)

        translation_dist = [-xmin, -ymin]

        if translation_dist[0] < 0 or translation_dist[1] < 0:
            translation_dist = [max(0, translation_dist[0]), max(0, translation_dist[1])]

        H_translation = np.array([
            [1, 0, translation_dist[0]],
            [0, 1, translation_dist[1]],
            [0, 0, 1]
        ])

        second_image_warped = cv2.warpPerspective(
            src=second_image,
            M=H_translation @ transformation_matrix,
            dsize=(xmax - xmin, ymax - ymin),
        )

        if (
            translation_dist[0] + w1 <= second_image_warped.shape[1]
            and translation_dist[1] + h1 <= second_image_warped.shape[0]
        ):
            second_image_warped[
                translation_dist[1]: translation_dist[1] + h1,
                translation_dist[0]: translation_dist[0] + w1,
            ] = first_image

        return second_image_warped

    def run(self):
        imgA_obj = Image.get_frame(self.imageA, self.redis_db)
        imgB_obj = Image.get_frame(self.imageB, self.redis_db)
        A = np.asarray(imgA_obj.value, dtype=np.uint8)
        B = np.asarray(imgB_obj.value, dtype=np.uint8)

        k_val = abs(int(round(self.knn_k))) if self.knn_k else 2
        reproj_error = abs(self.reproj_error) if self.reproj_error is not None else 3.0

        stitched = self.stitch_images(
            image1=A,
            image2=B,
            count_of_best_matches_per_query_descriptor=k_val,
            max_allowed_reprojection_error=reproj_error,
        )

        imgA_obj.value = stitched
        self.outputImage = Image.set_frame(
            imgA_obj, self.uID, self.redis_db
        )
        return build_response_stitch_images(self)


if __name__ == "__main__":
    Executor(sys.argv[1]).run()
