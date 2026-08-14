"""Terminal renderer for the candy crush board.

Provides `render_board(board, score=None, use_color=True)` which prints a simple
ASCII representation. Uses ANSI colors when available.
"""
from typing import List, Optional

_COLOR_MAP = {
    'r': '[31m',   # red
    'g': '[32m',   # green
    'y': '[33m',   # yellow
    'b': '[34m',   # blue
    'B': '[37m',   # box (white/grey)
    '#': '[90m',   # wall (dark grey)
}
_RESET = '[0m'


def _colorize(ch: str, use_color: bool) -> str:
    if not use_color or ch == ' ':
        return ch
    return _COLOR_MAP.get(ch, '') + ch + _RESET


def render_board(board: List[List[str]], score: Optional[int] = None, use_color: bool = True, moves_left = None, obstacles = None) -> None:
    """Print the board to stdout."""
    rows = len(board)
    cols = len(board[0]) if rows > 0 else 0

    print('\n   ' + ' '.join(str(c) for c in range(cols)))
    print('  +' + '-' * (2*cols-1) + '+')

    for r in range(rows):
        row_chars = [_colorize(board[r][c], use_color) for c in range(cols)]
        print(f"{r} |" + ' '.join(row_chars) + '|')

    print('  +' + '-' * (2*cols-1) + '+')
    
    if moves_left is not None:
        print(f'Moves left: {moves_left}')


    if obstacles is not None:
        print("Obstacles:", end=' ')
        if len(obstacles) == 0:
            print("None")
        else:
            print()
        for obstacle, count in obstacles.items():
            print(f'    {obstacle}: {count}')


    if score is not None:
        print(f'Score: {score}\n')


def animate_frames(frames, delay: float = 0.35, use_color: bool = True, step_mode: bool = False) -> None:
    """Play a list of (label, grid) frames in the terminal.

    step_mode=True: wait for Enter between frames (slo-mo debugging)
    instead of sleeping.
    """
    import time
    import sys

    total = len(frames)
    for i, frame in enumerate(frames):
        # accept both labeled tuples and bare grids
        label, grid = frame if isinstance(frame, tuple) else ("", frame)
        print('\033[H\033[J', end='')
        print(f"[frame {i + 1}/{total}] {label}")
        render_board(grid, use_color=use_color)
        sys.stdout.flush()
        if step_mode:
            if i < total - 1:
                input("-- Enter for next frame --")
        else:
            time.sleep(delay)
