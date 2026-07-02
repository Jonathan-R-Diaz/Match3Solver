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


def render_board(board: List[List[str]], score: Optional[int] = None, use_color: bool = True) -> None:
    """Print the board to stdout."""
    rows = len(board)
    cols = len(board[0]) if rows > 0 else 0

    print('\n   ' + ' '.join(str(c) for c in range(cols)))
    print('  +' + '--' * cols + '+')

    for r in range(rows):
        row_chars = [_colorize(board[r][c], use_color) for c in range(cols)]
        print(f"{r} |" + ' '.join(row_chars) + '|')

    print('  +' + '--' * cols + '+')
    if score is not None:
        print(f'Score: {score}\n')


def animate_frames(frames: List[List[List[str]]], delay: float = 0.35, use_color: bool = True) -> None:
    """Play a list of board frames in the terminal with a small delay."""
    import time
    import sys

    for frame in frames:
        print('\033[H\033[J', end='')
        render_board(frame, use_color=use_color)
        sys.stdout.flush()
        time.sleep(delay)
