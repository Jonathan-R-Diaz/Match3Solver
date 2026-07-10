import pytest
from candy_crush.fuzz import fuzz_game

# KNOWN BUG (backburner): powerup lines (e.g. three adjacent spinners) satisfy
# find_matches but pop() never clears powerup cells, so crush() loops forever.
# Seeds 6 and 15 hit it. Fix: exclude POWERUPS from line matching in
# find_matches (UNMATCHABLE constant is already defined in board.py).
_HANGING_SEEDS = {}


@pytest.mark.gameplay
@pytest.mark.parametrize("seed", [
    pytest.param(s, marks=pytest.mark.skip(reason="known crush() infinite loop — see comment above"))
    if s in _HANGING_SEEDS else s
    for s in range(25)
])
def test_fuzz_smoke(seed):
    # random 6x6 games with invariants enforced after every step
    failure = fuzz_game(seed, max_moves=30, rows=6, cols=6)
    assert failure is None, failure
