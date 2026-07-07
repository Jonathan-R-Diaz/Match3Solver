"""
Slice a Royal Kingdom screenshot into grid cells and save them for inspection.

Usage:
    python vision/calibrate.py [path/to/screenshot.png]

Grid bounds and dimensions are auto-detected from the gold board border.
"""
import sys
import os
import cv2

from vision.detect_grid import detect


def slice_board(img_path: str, out_dir: str = "vision/cells"):
    img = cv2.imread(img_path)
    assert img is not None, f"Could not load {img_path}"
    print(f"Image size: {img.shape[1]}×{img.shape[0]}")

    (x1, y1, x2, y2, rows, cols), overlay = detect(img, debug=True)
    print(f"Board: ({x1},{y1}) → ({x2},{y2})   Grid: {rows}×{cols}")

    board = img[y1:y2, x1:x2]
    cell_h = board.shape[0] // rows
    cell_w = board.shape[1] // cols

    os.makedirs(out_dir, exist_ok=True)
    for r in range(rows):
        for c in range(cols):
            cell = board[r * cell_h : (r + 1) * cell_h, c * cell_w : (c + 1) * cell_w]
            cv2.imwrite(f"{out_dir}/cell_{r}_{c}.png", cell)

    cv2.imwrite(f"{out_dir}/grid_overlay.png", overlay)
    print(f"Saved {rows * cols} cells + grid_overlay.png to {out_dir}/")


if __name__ == "__main__":
    img_path = sys.argv[1] if len(sys.argv) > 1 else "vision/screenshots/level_001.png"
    slice_board(img_path)
