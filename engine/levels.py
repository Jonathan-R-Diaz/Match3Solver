"""Level library: named board layouts for Game(board_state=..., fill_empty=True).

Each level is a list of row strings — far easier to keep aligned than nested
char lists. Symbols: '#'=wall, 'B'=box, 'C'=crate (2 hits, cracks into a
box), '.'=cell dealt a random candy.
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
    # vision/levels/level_002.png — 54 boxes, 30 moves; candies confined to
    # a 3-wide center channel, boxes reachable only from its edges
    2: [
        "BBB...BBB",
        "BBB...BBB",
        "BBB...BBB",
        "BBB...BBB",
        "BBB...BBB",
        "BBB...BBB",
        "BBB...BBB",
        "BBB...BBB",
        "BBB...BBB",
    ],
    # vision/levels/level_003.png — 45 crates, 32 moves; diagonal staircase
    # (crate wherever col <= row), candies in the upper-right triangle.
    # Crates, not boxes: the real screenshot's obstacle sprite takes 2 hits
    # (cracks into a box first), confirmed via vision template match.
    3: [
        "C........",
        "CC.......",
        "CCC......",
        "CCCC.....",
        "CCCCC....",
        "CCCCCC...",
        "CCCCCCC..",
        "CCCCCCCC.",
        "CCCCCCCCC",
    ],
}


# Natural move budget per level (matches the real screenshots levels 2/3
# were parsed from; level 1 has no source screenshot, 30 is just the
# original default). A generalist run needs this per-level, since a single
# global --moves would over- or under-budget whichever level it doesn't match.
LEVEL_MOVES = {1: 30, 2: 30, 3: 32}


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
