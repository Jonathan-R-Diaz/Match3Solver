"""Level library: named board layouts for Game(board_state=..., fill_empty=True).

Each level is a list of row strings — far easier to keep aligned than nested
char lists. Symbols: '#'=wall, 'B'=box, '.'=cell dealt a random candy.
Candies/powerups ('r','b','g','y','5','V','H','T','S') may be pre-placed.
"""
from typing import List

LEVELS = {
    1: [
        ".........",
        ".........",
        ".........",
        "BBBBBBBBB",
        "BBBBBBBBB",
        "BBBBBBBBB",
        "BBBBBBBBB",
        "BBBBBBBBB",
        "BBBBBBBBB",
    ],
}


def get_level(n: int) -> List[List[str]]:
    """Return level n as a fresh 2d grid (rows are validated for equal width)."""
    if n not in LEVELS:
        raise KeyError(f"no level {n}; available: {sorted(LEVELS)}")
    rows = LEVELS[n]
    width = len(rows[0])
    for i, row in enumerate(rows):
        if len(row) != width:
            raise ValueError(f"level {n} row {i} is {len(row)} wide, expected {width}")
    return [[' ' if ch == '.' else ch for ch in row] for row in rows]
