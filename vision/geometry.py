"""Where the board lives inside a screenshot."""
from dataclasses import dataclass


@dataclass
class GridGeometry:
    """Pixel layout of the board: top-left corner of the playfield, cell
    pitch, and grid dimensions. Produced by detect_grid for real screenshots
    (or synth for rendered ones) and consumed by executors to map moves back
    to screen coordinates."""

    x0: float
    y0: float
    cell_w: float
    cell_h: float
    rows: int
    cols: int

    def cell_center(self, r, c):
        """Pixel center of cell (r, c)."""
        return (self.x0 + (c + 0.5) * self.cell_w,
                self.y0 + (r + 0.5) * self.cell_h)
