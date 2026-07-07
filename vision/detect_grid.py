"""
Auto-detect board bounds and grid dimensions from a Royal Kingdom screenshot.

Strategy:
  - Board top/bottom: horizontal rows where >90% of pixels are gold (the thick border frame).
  - Board left/right: column extent of those same gold rows.
  - Row/col count: autocorrelation of the brightness profile within the board interior.

Returns (x1, y1, x2, y2, rows, cols) — all in image pixel coordinates.
"""
import cv2
import numpy as np


GOLD_LO = np.array([15, 150, 150])   # HSV lower bound for orange-gold
GOLD_HI = np.array([35, 255, 255])   # HSV upper bound for orange-gold

BORDER_THRESHOLD = 0.90   # fraction of a row that must be gold to count as the board border
SIDE_INSET_PX   = 8       # pixels to step inside the left/right border before treating as interior


def _gold_mask(img_bgr: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    return cv2.inRange(hsv, GOLD_LO, GOLD_HI)


def find_board_bounds(img_bgr: np.ndarray) -> tuple[int, int, int, int]:
    """
    Return (x1, y1, x2, y2) pixel bounds of the board interior (excluding the gold border).

    Raises RuntimeError if the border cannot be detected.
    """
    mask = _gold_mask(img_bgr)
    row_frac = mask.mean(axis=1) / 255.0          # fraction of gold per row

    dense_rows = np.where(row_frac > BORDER_THRESHOLD)[0]
    if len(dense_rows) < 2:
        raise RuntimeError(
            f"Expected 2 board borders with >{BORDER_THRESHOLD:.0%} gold coverage — "
            f"found {len(dense_rows)} row(s). Check GOLD_LO/HI or BORDER_THRESHOLD."
        )

    # Split dense rows into top-border group and bottom-border group
    # (any gap >100px separates them)
    gaps = np.where(np.diff(dense_rows) > 100)[0]
    if len(gaps) == 0:
        raise RuntimeError("Could not separate top and bottom gold borders.")

    top_group = dense_rows[: gaps[0] + 1]
    bot_group = dense_rows[gaps[0] + 1 :]

    y_top_end   = int(top_group[-1])    # last row of the top gold band
    y_bot_start = int(bot_group[0])     # first row of the bottom gold band

    # Find horizontal extent from within the top gold band
    gold_band = img_bgr[top_group[0] : y_top_end + 1, :]
    band_mask = _gold_mask(gold_band)
    col_coverage = band_mask.mean(axis=0)                  # mean over band rows
    gold_cols = np.where(col_coverage > 127)[0]
    if len(gold_cols) == 0:
        raise RuntimeError("Could not find horizontal extent of the gold top border.")

    x1_border = int(gold_cols[0])
    x2_border = int(gold_cols[-1])

    # Interior: just inside the borders
    x1 = x1_border + SIDE_INSET_PX
    x2 = x2_border - SIDE_INSET_PX
    y1 = y_top_end + 1
    y2 = y_bot_start - 1

    return x1, y1, x2, y2


def _autocorr_count(signal: np.ndarray, min_cells: int = 5, max_cells: int = 14) -> int:
    """
    Pick the cell count whose period maximises the mean autocorrelation of `signal`.
    """
    n = len(signal)
    sig = signal - signal.mean()
    best_count, best_score = min_cells, float("-inf")
    for cells in range(min_cells, max_cells + 1):
        period = n / cells
        if period < 1:
            continue
        scores = []
        for k in range(1, cells):
            lag = int(round(k * period))
            if lag >= n:
                break
            scores.append(float(np.dot(sig[: n - lag], sig[lag:])))
        score = float(np.mean(scores)) if scores else float("-inf")
        if score > best_score:
            best_score = score
            best_count = cells
    return best_count


def find_grid_size(img_bgr: np.ndarray, x1: int, y1: int, x2: int, y2: int) -> tuple[int, int]:
    """Return (rows, cols) by autocorrelating brightness profiles inside the board."""
    board = img_bgr[y1:y2, x1:x2]
    gray  = cv2.cvtColor(board, cv2.COLOR_BGR2GRAY).astype(float)
    rows = _autocorr_count(gray.mean(axis=1))
    cols = _autocorr_count(gray.mean(axis=0))
    return rows, cols


def detect(
    img_bgr: np.ndarray,
    debug: bool = False,
) -> tuple:
    """
    Full pipeline: BGR image → (x1, y1, x2, y2, rows, cols).

    If debug=True, returns ((x1, y1, x2, y2, rows, cols), overlay_img).
    """
    x1, y1, x2, y2 = find_board_bounds(img_bgr)
    rows, cols = find_grid_size(img_bgr, x1, y1, x2, y2)

    if debug:
        overlay = img_bgr.copy()
        board_h = y2 - y1
        board_w = x2 - x1
        cell_h = board_h // rows
        cell_w = board_w // cols
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 255, 0), 3)
        for r in range(rows + 1):
            y = y1 + r * cell_h
            cv2.line(overlay, (x1, y), (x2, y), (0, 255, 0), 1)
        for c in range(cols + 1):
            x = x1 + c * cell_w
            cv2.line(overlay, (x, y1), (x, y2), (0, 255, 0), 1)
        return (x1, y1, x2, y2, rows, cols), overlay

    return x1, y1, x2, y2, rows, cols


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "vision/screenshots/level_001.png"
    img = cv2.imread(path)
    if img is None:
        raise SystemExit(f"Could not load {path}")
    (x1, y1, x2, y2, rows, cols), overlay = detect(img, debug=True)
    print(f"Board interior: ({x1},{y1}) → ({x2},{y2})   Grid: {rows}×{cols}")
    out = "vision/cells/auto_detect_overlay.png"
    cv2.imwrite(out, overlay)
    print(f"Overlay saved to {out}")
