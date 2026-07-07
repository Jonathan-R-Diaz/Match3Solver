"""
Per-cell classifier for Royal Kingdom board cells.

Maps a cropped cell image → one of the Board symbols defined in candy_crush.board.
Candy order in CANDIES is [red, blue, green, yellow].
Non-candy symbols: 'B' (box obstacle), ' ' (empty).

Classification is pure HSV: mask background, measure median hue of foreground.
Hue boundaries derived from measured game samples:
  red H≈1, box H≈14, yellow H≈22, green H≈61, blue H≈107
"""
import cv2
import numpy as np

from candy_crush.board import CANDIES

# CANDIES = ["r", "b", "g", "y"] — symbols must match board.py
_RED, _BLUE, _GREEN, _YELLOW = CANDIES

# Background: low-saturation OR blue-grey with low saturation
_BG_SAT_MAX = 60
_BG_HUE_LO  = 90
_BG_HUE_HI  = 140
_BG_SAT_BLUE = 100   # blue-grey background has moderate saturation

# Foreground fraction below which we call a cell empty
_EMPTY_THRESHOLD = 0.15

# Hue ranges (OpenCV H scale 0-180): sorted boundaries between classes
# Anything outside these ranges falls into the nearest bucket.
#   H  0-8   → red diamond  '$'
#   H  9-18  → box          'B'
#   H  19-30 → yellow dome  '%'
#   H  50-75 → green clover '&'
#   H  90-120→ blue tower   '@'
_HUE_CLASSES = [
    (0,   8,   _RED),    # red diamond
    (9,   18,  'B'),     # box obstacle
    (19,  30,  _YELLOW), # yellow dome
    (50,  75,  _GREEN),  # green clover
    (90,  120, _BLUE),   # blue tower
]


def classify_cell(img_bgr: np.ndarray) -> str:
    """
    Return the Board symbol for a single cropped cell image.

    Args:
        img_bgr: BGR image of one cell (any size).
    Returns:
        One of '$', '%', '&', '@', 'B', ' '.
    """
    h, w = img_bgr.shape[:2]
    # Center 60% crop to avoid background bleed from cell edges
    crop = img_bgr[int(h * 0.2): int(h * 0.8),
                   int(w * 0.2): int(w * 0.8)]
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV).astype(np.float32)

    sat  = hsv[:, :, 1]
    hue  = hsv[:, :, 0]

    bg_mask = (sat < _BG_SAT_MAX) | (
        (hue >= _BG_HUE_LO) & (hue <= _BG_HUE_HI) & (sat < _BG_SAT_BLUE)
    )

    total = bg_mask.size
    fg_count = int((~bg_mask).sum())
    if fg_count / total < _EMPTY_THRESHOLD:
        return ' '

    fg_hue = hue[~bg_mask]
    med_h  = float(np.median(fg_hue))

    for lo, hi, symbol in _HUE_CLASSES:
        if lo <= med_h <= hi:
            return symbol

    # Fallback: nearest class by midpoint distance
    midpoints = [(lo + hi) / 2 for lo, hi, _ in _HUE_CLASSES]
    closest = min(range(len(midpoints)), key=lambda i: abs(midpoints[i] - med_h))
    return _HUE_CLASSES[closest][2]


def classify_board(
    img_bgr: np.ndarray,
    x1: int, y1: int, x2: int, y2: int,
    rows: int, cols: int,
) -> list[list[str]]:
    """
    Slice the full screenshot into cells and classify each one.

    Returns a 2-D list of Board symbols (rows × cols).
    """
    board_crop = img_bgr[y1:y2, x1:x2]
    cell_h = board_crop.shape[0] // rows
    cell_w = board_crop.shape[1] // cols

    grid = []
    for r in range(rows):
        row = []
        for c in range(cols):
            cell = board_crop[r * cell_h: (r + 1) * cell_h,
                              c * cell_w: (c + 1) * cell_w]
            row.append(classify_cell(cell))
        grid.append(row)
    return grid


if __name__ == "__main__":
    import sys
    from vision.detect_grid import detect

    path = sys.argv[1] if len(sys.argv) > 1 else "vision/screenshots/level_001.png"
    img = cv2.imread(path)
    (x1, y1, x2, y2, rows, cols) = detect(img)
    grid = classify_board(img, x1, y1, x2, y2, rows, cols)

    # Pretty-print
    candy_names = {_RED: 'red', _YELLOW: 'yel', _GREEN: 'grn', _BLUE: 'blu', 'B': 'BOX', ' ': '   '}
    print(f"Detected {rows}×{cols} board:\n")
    for row in grid:
        print("  " + "  ".join(candy_names.get(c, '???') for c in row))
