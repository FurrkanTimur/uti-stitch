import os
import numpy as np
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../../../../"))

from sdks.novavision.src.base.component import Component
from sdks.novavision.src.base.model import Detection
from sdks.novavision.src.helper.executor import Executor
from components.Stitch.src.utils.response_stitch_ocr import build_response_stitch_ocr
from components.Stitch.src.models.PackageModel import PackageModel
from components.Stitch.src.models.StitchOcrModel import OCRDetection


class StitchOcr(Component):
    def __init__(self, request, bootstrap):
        super().__init__(request, bootstrap)
        self.request.model = PackageModel(**(self.request.data))

        self.ocr_detections = self.request.get_param("inputDetections")

        self.reading_direction = self.request.get_param("ReadingDirection")
        self.tolerance = self.request.get_param("Tolerance")
        self.cluster_distance = self.request.get_param("ClusterDistance")

        print(self.reading_direction, self.tolerance, self.cluster_distance)

    @staticmethod
    def bootstrap(config: dict) -> dict:
        return {}

    def stitch_ocr_detections(self) -> list[dict]:
        if not self.ocr_detections or len(self.ocr_detections) == 0:
            return []

        boxes = []
        texts = []

        for detection in self.ocr_detections:
            bbox = detection.get("boundingBox", {})
            text = detection.get("data", "")

            x = bbox.get("left", 0)
            y = bbox.get("top", 0)
            w = bbox.get("width", 0)
            h = bbox.get("height", 0)

            boxes.append((x, y, w, h))
            texts.append(text)

        xyxy = np.array([[x, y, x + w, y + h] for x, y, w, h in boxes])

        reading_direction = self.reading_direction
        if reading_direction == "auto":
            reading_direction = self._detect_reading_direction(xyxy)

        clusters = self._cluster_detections(xyxy, self.cluster_distance)

        results = []
        for cluster_indices in clusters:
            cluster_xyxy = xyxy[cluster_indices]
            cluster_texts = [texts[i] for i in cluster_indices]

            stitched_text = self._stitch_cluster(
                cluster_xyxy, cluster_texts, reading_direction
            )

            # calculate bounding box for the entire cluster
            min_x = np.min(cluster_xyxy[:, 0])
            min_y = np.min(cluster_xyxy[:, 1])
            max_x = np.max(cluster_xyxy[:, 2])
            max_y = np.max(cluster_xyxy[:, 3])

            results.append(
                OCRDetection(
                    boundingBox={
                        "left": int(min_x),
                        "top": int(min_y),
                        "width": int(max_x - min_x),
                        "height": int(max_y - min_y),
                    },
                    confidence=0.0,
                    classLabel="",
                    classId=0,
                    data=stitched_text,
                )
            )

        return results

    def _cluster_detections(
        self, xyxy: np.ndarray, max_distance: float
    ) -> list[list[int]]:
        n = len(xyxy)
        if n == 0:
            return []

        # centers of bounding boxes
        centers = np.column_stack(
            [(xyxy[:, 0] + xyxy[:, 2]) / 2, (xyxy[:, 1] + xyxy[:, 3]) / 2]
        )

        # which detections have been assigned to clusters
        assigned = np.zeros(n, dtype=bool)
        clusters = []

        for i in range(n):
            if assigned[i]:
                continue

            cluster = [i]
            assigned[i] = True

            # find all detections close
            changed = True
            while changed:
                changed = False
                for j in range(n):
                    if assigned[j]:
                        continue

                    # check distance
                    for cluster_idx in cluster:
                        dist = np.linalg.norm(centers[j] - centers[cluster_idx])
                        if dist <= max_distance:
                            cluster.append(j)
                            assigned[j] = True
                            changed = True
                            break

            clusters.append(cluster)

        return clusters

    def _stitch_cluster(
        self, xyxy: np.ndarray, texts: list[str], reading_direction: str
    ) -> str:
        xyxy_prepared = self._prepare_coordinates(xyxy, reading_direction)

        boxes_by_line = self._group_detections_by_line(
            xyxy_prepared, reading_direction, self.tolerance
        )

        lines = sorted(
            boxes_by_line.keys(),
            reverse=(reading_direction == "vertical_bottom_to_top"),
        )

        ordered_texts = []
        delimiter = " "

        for i, key in enumerate(lines):
            line_data = boxes_by_line[key]
            line_xyxy = np.array(line_data["xyxy"])
            line_idx = np.array(line_data["idx"])

            sort_idx = self._sort_line_detections(line_xyxy, reading_direction)

            ordered_texts.extend([texts[idx] for idx in line_idx[sort_idx]])

            if i < len(lines) - 1:
                ordered_texts.append(self._get_line_separator(reading_direction))

        return delimiter.join(ordered_texts)

    def _detect_reading_direction(self, xyxy: np.ndarray) -> str:
        if len(xyxy) == 0:
            return "left_to_right"

        widths = xyxy[:, 2] - xyxy[:, 0]
        heights = xyxy[:, 3] - xyxy[:, 1]

        avg_width = np.mean(widths)
        avg_height = np.mean(heights)

        if avg_width > avg_height:
            return "left_to_right"
        else:
            return "vertical_top_to_bottom"

    def _prepare_coordinates(
        self, xyxy: np.ndarray, reading_direction: str
    ) -> np.ndarray:
        if reading_direction in ["vertical_top_to_bottom", "vertical_bottom_to_top"]:
            return xyxy[:, [1, 0, 3, 2]]
        return xyxy

    def _group_detections_by_line(
        self, xyxy: np.ndarray, reading_direction: str, tolerance: int
    ) -> dict[int, dict[str, list]]:
        # After prepare_coordinates swap, a line's vertical span is always [:, 1]-[:, 3].
        # Detections on the same visual line naturally overlap in this range (ascenders/
        # descenders), while separate lines don't - so group by vertical range overlap
        # instead of a fixed rounding grid, which split same-line words across grid
        # boundaries and merged them onto the wrong line.
        order = np.argsort(xyxy[:, 1])
        lines = []  # each: {"y_min", "y_max", "idx": [...]}

        for i in order:
            y1, y2 = xyxy[i, 1], xyxy[i, 3]

            best_line = None
            best_gap = None
            for line in lines:
                gap = max(y1, line["y_min"]) - min(y2, line["y_max"])
                if gap <= tolerance and (best_gap is None or gap < best_gap):
                    best_line = line
                    best_gap = gap

            if best_line is None:
                lines.append({"y_min": y1, "y_max": y2, "idx": [i]})
            else:
                best_line["idx"].append(i)
                best_line["y_min"] = min(best_line["y_min"], y1)
                best_line["y_max"] = max(best_line["y_max"], y2)

        boxes_by_line = {}
        for key, line in enumerate(lines):
            boxes_by_line[key] = {
                "xyxy": [xyxy[i] for i in line["idx"]],
                "idx": line["idx"],
            }

        return boxes_by_line

    def _sort_line_detections(
        self, line_xyxy: np.ndarray, reading_direction: str
    ) -> np.ndarray:
        # After prepare_coordinates swap, we always sort by x ([:, 0])
        if reading_direction in ["left_to_right", "vertical_top_to_bottom"]:
            return line_xyxy[:, 0].argsort()
        else:  # right_to_left or vertical_bottom_to_top
            return (-line_xyxy[:, 0]).argsort()

    def _get_line_separator(self, reading_direction: str) -> str:
        return "\n" if reading_direction in ["left_to_right", "right_to_left"] else " "

    def run(self):
        stitched_results = self.stitch_ocr_detections()
        self.stitched = stitched_results

        packageModel = build_response_stitch_ocr(context=self)
        return packageModel


if "__main__" == __name__:
    Executor(sys.argv[1]).run()
