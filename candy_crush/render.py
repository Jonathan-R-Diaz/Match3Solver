"""Terminal renderer for the candy crush board.

Provides `render_board(board, score=None, use_color=True)` which prints a simple
ASCII representation. Uses ANSI colors when available.
"""
from typing import List, Optional

# ANSI color codes mapped to candy symbols (fallback to white)
_COLOR_MAP = {
    '$': '\u001b[33m',
    '%': '\u001b[31m',
    '&': '\u001b[35m',
    '@': '\u001b[32m',
    '*': '\u001b[36m',
}
_RESET = '\u001b[0m'


def _colorize(ch: str, use_color: bool) -> str:
    if not use_color or ch == ' ':
        return ch
    return _COLOR_MAP.get(ch, '') + ch + _RESET


def render_board(board: List[List[str]], score: Optional[int] = None, use_color: bool = True) -> None:
    """Print the board to stdout.

    board: 2D list of single-character symbols.
    """
    rows = len(board)
    cols = len(board[0]) if rows > 0 else 0

    # Header
    print('\n   ' + ' '.join(str(c) for c in range(cols)))
    print('  +' + '--' * cols + '+')

    for r in range(rows):
        row_chars = []
        for c in range(cols):
            ch = board[r][c]
            row_chars.append(_colorize(ch, use_color))
        print(f"{r} |" + ' '.join(row_chars) + '|')

    print('  +' + '--' * cols + '+')
    if score is not None:
        print(f'Score: {score}\n')


if __name__ == '__main__':
    # Quick demo when run directly
    demo_board = [
        ['$', '#', '&', '@', '*'],
        ['#', '$', '&', '@', '*'],
        ['&', '&', '&', '$', '#'],
    ]
    render_board(demo_board, score=42)


def animate_frames(frames: List[List[List[str]]], delay: float = 0.35, use_color: bool = True) -> None:
    """Play a list of board frames in the terminal with a small delay.

    Each frame is a 2D list of characters identical to `board`.
    """
    import time
    import os

    def _clear():
        # Try a fast ANSI clear which works in most terminals
        print('\033[H\033[J', end='')

    # Play frames
    import sys

    for frame in frames:
        _clear()
        render_board(frame, use_color=use_color)
        # Ensure output is shown immediately
        sys.stdout.flush()
        time.sleep(delay)
