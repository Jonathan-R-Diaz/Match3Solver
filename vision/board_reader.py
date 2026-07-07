"""
Full pipeline: screenshot → Board-compatible board_state.

    from vision.board_reader import read_board_from_file, read_board_live

    # From a saved screenshot
    board_state = read_board_from_file("vision/screenshots/level_001.png")

    # From the connected Android phone via ADB
    board_state = read_board_live()
"""
import subprocess
import tempfile
import os
import cv2

from vision.detect_grid import detect
from vision.classify import classify_board


def read_board_from_file(img_path: str) -> list[list[str]]:
    """Load a saved screenshot and return a board_state grid."""
    img = cv2.imread(img_path)
    if img is None:
        raise FileNotFoundError(img_path)
    x1, y1, x2, y2, rows, cols = detect(img)
    return classify_board(img, x1, y1, x2, y2, rows, cols)


def read_board_live(device: str | None = None) -> list[list[str]]:
    """
    Capture a screenshot from the connected Android device via ADB and
    return the classified board_state.

    Raises RuntimeError if ADB fails or no device is found.
    """
    adb = ["adb"] + (["-s", device] if device else [])

    result = subprocess.run(
        adb + ["shell", "screencap", "-p", "/sdcard/_cc_snap.png"],
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ADB screencap failed: {result.stderr.decode()}")

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            adb + ["pull", "/sdcard/_cc_snap.png", tmp_path],
            capture_output=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"ADB pull failed: {result.stderr.decode()}")
        return read_board_from_file(tmp_path)
    finally:
        os.unlink(tmp_path)


if __name__ == "__main__":
    import sys
    from candy_crush.game import Game
    from candy_crush.render import render_board

    if len(sys.argv) > 1:
        board_state = read_board_from_file(sys.argv[1])
    else:
        print("Capturing live screenshot via ADB...")
        board_state = read_board_live()

    game = Game(board_state=board_state)
    render_board(game.board.get_board())
