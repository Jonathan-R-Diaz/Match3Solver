"""Screenshot -> board grid in the engine's alphabet.

Two readers, one interface (read(img) -> grid, .geometry for gestures):

  AutoBoardReader — real Royal Kingdom screenshots. detect_grid.py finds the
      board by its gold border, classify.py names each cell by HSV hue.
      Nothing to calibrate.
  BoardReader — synth.py's rendered boards (the sim loop and tests), matched
      against a flat-color palette.
"""
import numpy as np


class AutoBoardReader:
    """self.geometry is set after the first read(), mapping board cells back
    to screen pixels for the executor."""

    def __init__(self):
        self.geometry = None

    def read(self, img):
        from vision.detect_grid import detect
        from vision.classify import classify_board
        from vision.geometry import GridGeometry

        bgr = np.asarray(img.convert("RGB"))[:, :, ::-1].copy()
        x1, y1, x2, y2, rows, cols = detect(bgr)
        self.geometry = GridGeometry(
            x0=x1, y0=y1, cell_w=(x2 - x1) / cols, cell_h=(y2 - y1) / rows,
            rows=rows, cols=cols)
        return classify_board(bgr, x1, y1, x2, y2, rows, cols)


class BoardReader:
    """Samples the mean color of each cell's central patch and classifies it
    against a palette.

    patch: fraction of the cell used for sampling — small enough to dodge
    cell borders, big enough to average over texture.
    """

    def __init__(self, geometry, palette, patch=0.4):
        self.geometry = geometry
        self.palette = palette
        self.patch = patch

    def _patch_mean(self, arr, r, c):
        cx, cy = self.geometry.cell_center(r, c)
        half_w = self.geometry.cell_w * self.patch / 2
        half_h = self.geometry.cell_h * self.patch / 2
        y0 = int(cy - half_h)
        x0 = int(cx - half_w)
        y1 = max(int(cy + half_h), y0 + 1)
        x1 = max(int(cx + half_w), x0 + 1)
        return arr[y0:y1, x0:x1].reshape(-1, 3).mean(axis=0)

    def read(self, img):
        """Parse the whole board. Returns a list-of-lists grid of symbols.
        Raises UnknownCellError on any cell the palette can't name."""
        arr = np.asarray(img.convert("RGB"), dtype=float)
        return [[self.palette.classify(self._patch_mean(arr, r, c), r, c)
                 for c in range(self.geometry.cols)]
                for r in range(self.geometry.rows)]
