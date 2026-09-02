import os
import cv2
import sys
import math
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

from sdks.novavision.src.media.image import Image
from sdks.novavision.src.base.component import Component
from sdks.novavision.src.helper.executor import Executor
from components.Stitch.src.utils.response_on_edge import build_response_on_edge
from components.Stitch.src.models.PackageModel import PackageModel


class OnEdge(Component):
    def __init__(self, request, bootstrap):
        super().__init__(request, bootstrap)
        self.request.model = PackageModel(**(self.request.data))
        self.images = self.request.get_param("inputImages")
        self.row_mode = self.request.get_param("configRow")
        self.column_mode = self.request.get_param("configColumn")
        self.max_frames = self.request.get_param("configMaxFrames")
        self.cell_width = self.request.get_param("configCellWidth")
        if self.row_mode == "Fixed":
            self.row_count = self.request.get_param("configRowCount")
        if self.column_mode == "Fixed":
            self.column_count = self.request.get_param("configColumnCount")

    @staticmethod
    def bootstrap(config: dict) -> dict:
        return {}

    @staticmethod
    def resample(frames, target_count):
        """Pick target_count frames spread evenly across the whole sequence."""
        n = len(frames)
        if target_count >= n:
            return frames
        if target_count <= 1:
            return [frames[0]]
        return [frames[round(k * (n - 1) / (target_count - 1))] for k in range(target_count)]

    def resolve_grid(self, count):
        """
        Turn the two axis settings into a concrete (rows, columns) pair that
        holds at least `count` cells. A "Max" axis grows to fit whatever the
        pinned axis leaves over; two "Max" axes fall back to a near-square.
        """
        row_fixed = self.row_mode == "Fixed"
        column_fixed = self.column_mode == "Fixed"

        if row_fixed and column_fixed:
            return self.row_count, self.column_count
        if column_fixed:
            columns = self.column_count
            return math.ceil(count / columns), columns
        if row_fixed:
            rows = self.row_count
            return rows, math.ceil(count / rows)

        columns = math.ceil(math.sqrt(count))
        return math.ceil(count / columns), columns

    def build_collage(self, frames):
        rows, columns = self.resolve_grid(len(frames))

        # Both axes pinned: the grid itself is the cap, so thin the sequence
        # down to what fits instead of letting the tail fall off the end.
        capacity = rows * columns
        if len(frames) > capacity:
            frames = self.resample(frames, capacity)

        height, width = frames[0].shape[:2]
        cell_w = int(self.cell_width)
        cell_h = max(1, int(round(cell_w * height / width)))

        cells = [cv2.resize(frame, (cell_w, cell_h)) for frame in frames]

        channels = cells[0].shape[2] if cells[0].ndim == 3 else 1
        blank = np.zeros((cell_h, cell_w, channels), dtype=np.uint8) if channels > 1 \
            else np.zeros((cell_h, cell_w), dtype=np.uint8)

        # Pad the tail so every row hstacks to the same width.
        cells.extend([blank] * (rows * columns - len(cells)))

        return np.vstack([
            np.hstack(cells[r * columns:(r + 1) * columns])
            for r in range(rows)
        ])

    def run(self):
        # This node sits behind a filter, so on the vast majority of frames there is
        # simply no event to render: nothing upstream matched and the input arrives
        # empty. That is the normal idle path, not an error - emit an empty output and
        # let the flow carry on.
        images = self.images if isinstance(self.images, list) else [self.images]
        image_objs = [
            frame for frame in (Image.get_frame(img, self.redis_db) for img in images if img)
            if frame is not None and getattr(frame, "value", None) is not None
        ]

        if not image_objs:
            self.outputImage = []
            return build_response_on_edge(self)

        frames = [np.asarray(obj.value, dtype=np.uint8) for obj in image_objs]

        frames = self.resample(frames, int(self.max_frames))
        collage = self.build_collage(frames)

        carrier = image_objs[0]
        carrier.value = collage
        self.outputImage = Image.set_frame(carrier, self.uID, self.redis_db)
        return build_response_on_edge(self)


if __name__ == "__main__":
    Executor(sys.argv[1]).run()
