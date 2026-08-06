#!/usr/bin/env python3
"""Drive a real Royal Kingdom board with a trained checkpoint. The board is
auto-detected from its gold border — nothing to calibrate. Run from repo root.

Default mode (phone plugged in over USB with adb debugging): screenshots the
device, prints the board it sees with the suggested move, and waits — you
make the move in the game, press Enter when the board is ready, and it
screenshots again for the next move:

    python vision/play_live.py                       # uses the level-1 ckpt
    python vision/play_live.py models/other.pt       # or name one

Variants:

    --watch     no Enter needed — polls the screen and moves on by itself
                once the board visibly changes and settles
    --execute   full automation: performs the moves too (adb swipe/tap)
    --image X   no adb: read a screenshot file you took yourself, or watch
                a folder for new ones

Pipeline check without any device — the agent plays the engine while seeing
only rendered frames:

    python vision/play_live.py models/reinforce_level1.pt --sim --moves 15
"""
import sys
import time
from argparse import ArgumentParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine.render import _COLOR_MAP as ENGINE_COLORS
from vision import (AdbCapture, AdbExecutor, AutoBoardReader, FileCapture,
                    PolicyAgent, SuggestExecutor, UnknownCellError)
from vision.executor import DESCRIBE


# the engine's own candy/box colors, plus bright+bold for the powerups the
# engine renderer doesn't color
_POWERUP_COLORS = {
    "5": "\033[95;1m",  # light ball — bright magenta
    "V": "\033[91;1m",  # vertical rocket — bright red
    "H": "\033[96;1m",  # horizontal rocket — bright cyan
    "T": "\033[93;1m",  # TNT — bright yellow
    "S": "\033[92;1m",  # propeller — bright green
}
_MARK = "\033[1m"       # bold brackets around the suggested move's cells
_RESET = "\033[0m"


def _paint(ch):
    color = _POWERUP_COLORS.get(ch) or ENGINE_COLORS.get(ch, "")
    return f"{color}{ch}{_RESET}" if color else ch


def show_board(grid, move=None):
    """Print the parsed board in color; bracket the cells the move touches."""
    marked = set()
    if move:
        r, c, d = move
        marked.add((r, c))
        if d == "s":
            marked.add((r + 1, c))
        elif d == "d":
            marked.add((r, c + 1))
    print("    " + "  ".join(f"{c}" for c in range(len(grid[0]))))
    for r, row in enumerate(grid):
        cells = [f"{_MARK}[{_RESET}{_paint(ch)}{_MARK}]{_RESET}"
                 if (r, c) in marked else f" {_paint(ch)} "
                 for c, ch in enumerate(row)]
        print(f" {r} " + "".join(cells))


# anchored next to this file so it works no matter where it's launched from
LAST_FRAME = Path(__file__).resolve().parent / "screenshots" / \
    "last_frame.png"


def grab_and_save(capture):
    """Screenshot the phone and keep it at vision/screenshots/last_frame.png
    (folder created if needed) — saved before any parsing, so a frame with an
    unrecognized powerup is already on disk for scripts/add_template.py."""
    frame = capture.grab()
    LAST_FRAME.parent.mkdir(parents=True, exist_ok=True)
    frame.save(LAST_FRAME)
    return frame


def suggest_once(img, reader, agent, make_executor):
    """Parse one frame, print what the bot sees, and emit its move.
    Returns (grid, move); move is None on a stalemate."""
    grid = reader.read(img)
    move = agent.pick(grid)
    show_board(grid, move)
    if move is None:
        print(">>> no legal moves on the parsed board — misread, or the "
              "game is about to reshuffle")
        return grid, None
    make_executor(reader.geometry).execute(*move)
    return grid, move


def wait_for_new_board(capture, reader, prev_grid, poll=1.0):
    """Poll the screen until the board has changed AND settled (two
    consecutive identical parses), so a mid-cascade frame is never fed to
    the agent. Unreadable frames (animations, popups) are skipped."""
    last = None
    while True:
        time.sleep(poll)
        try:
            grid = reader.read(capture.grab())
        except (UnknownCellError, RuntimeError):
            last = None  # unreadable — wait for the screen to calm down
            continue
        if grid != prev_grid and grid == last:
            return grid
        last = grid


def run_sim(args):
    """Full episodes against the engine, seen only through rendered images."""
    from rl.env import CandyCrushEnv
    from vision import BoardReader, render_board, synth_palette
    from vision.synth import synth_geometry

    env = CandyCrushEnv(level=args.level, max_moves=args.moves,
                        seed=args.seed)
    obs, info = env.reset()
    geo = synth_geometry(env.rows, env.cols)
    reader = BoardReader(geo, synth_palette())
    agent = PolicyAgent(args.model)
    start = info["obstacles"]

    while True:
        frame = render_board(env.game.board.grid, geo)
        grid = reader.read(frame)  # the agent only ever sees the image
        move = agent.pick(grid)
        if move is None:
            print(f"stalemate — cleared {start - info['obstacles']}/{start} "
                  f"obstacles")
            return
        show_board(grid, move)
        r, c, d = move
        print(f">>> {DESCRIBE[d]} at ({r},{c})\n")
        _, _, terminated, truncated, info = env.step(
            env.encode_action(r, c, d))
        if terminated or truncated:
            break

    outcome = "WIN" if info["is_success"] else \
              ("stalemate" if terminated else "out of moves")
    print(f"{outcome} — cleared {start - info['obstacles']}/{start} "
          f"obstacles, seen entirely through the vision pipeline")


def main():
    parser = ArgumentParser()
    parser.add_argument('model', nargs='?',
                        default=str(Path(__file__).resolve().parent.parent /
                                    "models" / "reinforce_level2.pt"),
                        help='checkpoint (.pt) from train.py')
    parser.add_argument('--image',
                        help='screenshot file, or a folder to watch for new '
                             'screenshots (instead of capturing over adb)')
    parser.add_argument('--serial', default=None, help='adb device serial')
    parser.add_argument('--watch', action='store_true',
                        help='instead of Enter-pacing, poll the screen and '
                             'suggest as soon as the board changes')
    parser.add_argument('--execute', action='store_true',
                        help='perform moves on the device too via adb '
                             '(default only suggests)')
    parser.add_argument('--settle', type=float, default=5.0,
                        help='seconds to wait after an executed move for '
                             'cascades to finish')
    parser.add_argument('--sim', action='store_true',
                        help='no device: play the engine through rendered '
                             'frames (pipeline self-test)')
    parser.add_argument('--level', type=int, default=1, help='sim level')
    parser.add_argument('--moves', type=int, default=30, help='sim moves')
    parser.add_argument('--seed', type=int, default=0, help='sim seed')
    args = parser.parse_args()

    if args.sim:
        run_sim(args)
        return

    reader = AutoBoardReader()
    agent = PolicyAgent(args.model)

    if not args.image:  # default: capture from the phone over adb
        from vision.capture import CaptureError, wait_for_device
        serial = wait_for_device(args.serial)
        print(f"phone ready ({serial})\n")
        capture = AdbCapture(serial=serial)
        make_executor = ((lambda geo: AdbExecutor(geo, serial=serial))
                         if args.execute else SuggestExecutor)
        grid = None
        while True:
            try:
                grid, move = suggest_once(grab_and_save(capture), reader,
                                          agent, make_executor)
            except CaptureError as e:  # adb hiccup — wonky cable/phone
                print(f"capture failed ({e})")
                wait_for_device(serial)
                continue
            except (UnknownCellError, RuntimeError) as e:
                print(f"unreadable frame ({e})")
                input("press Enter to try another screenshot... ")
                continue
            if move is None:
                break
            if args.execute:
                time.sleep(args.settle)
            elif args.watch:
                print("make the move — watching the screen for the result...")
                wait_for_new_board(capture, reader, grid)
            else:
                input("\nmake the move, then press Enter for the next "
                      "screenshot... ")
                print()
        return

    capture = FileCapture(args.image)
    watching = Path(args.image).is_dir()
    while True:
        try:
            suggest_once(capture.grab(), reader, agent, SuggestExecutor)
        except (UnknownCellError, RuntimeError) as e:
            print(f"could not read that screenshot: {e}")
        if not watching:
            break
        print("\nwaiting for the next screenshot... (Ctrl-C to stop)")


if __name__ == "__main__":
    main()
