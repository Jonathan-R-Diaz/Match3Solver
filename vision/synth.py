"""Render a board grid to an image. Powers the tests and the --sim loop:
the agent plays the engine while seeing only these rendered frames, which
proves the image->board->move pipeline end to end without a device."""
from PIL import Image, ImageDraw

from vision.geometry import GridGeometry
from vision.palette import SYNTH_SWATCHES

BG = (25, 25, 30)


def synth_geometry(rows, cols, cell=48, margin=24):
    """Geometry matching render_board's layout for a rows x cols grid."""
    return GridGeometry(x0=margin, y0=margin, cell_w=cell, cell_h=cell,
                        rows=rows, cols=cols)


def render_board(grid, geometry=None):
    """Draw each cell as a flat swatch-colored tile. Returns a PIL Image."""
    rows, cols = len(grid), len(grid[0])
    geo = geometry or synth_geometry(rows, cols)
    width = int(geo.x0 * 2 + geo.cell_w * cols)
    height = int(geo.y0 * 2 + geo.cell_h * rows)
    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)
    gap = 2  # thin border so tiles read as a grid, like the real game
    for r in range(rows):
        for c in range(cols):
            color = tuple(int(v) for v in SYNTH_SWATCHES[grid[r][c]])
            x = geo.x0 + c * geo.cell_w
            y = geo.y0 + r * geo.cell_h
            draw.rectangle([x + gap, y + gap,
                            x + geo.cell_w - gap, y + geo.cell_h - gap],
                           fill=color)
    return img
