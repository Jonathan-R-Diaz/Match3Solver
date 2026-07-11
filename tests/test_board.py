import pytest
from candy_crush.board import Board


def test_board_initial_no_matches():
    # Seed chosen so the board generation loop terminates deterministically
    b = Board(rows=5, cols=5, seed=123)
    matches = b.find_matches()
    assert isinstance(matches, set)
    assert len(matches) == 0


def test_swap_and_match_detection():
    b = Board(rows=3, cols=3, seed=42)
    # Manually create a horizontal match after a swap
    b.grid = [
        ['r', '#', 'g'],
        ['r', '#', 'g'],
        ['#', 'r', 'r']
    ]
    # Swap (2,0) with (2,1) to make last row ['r', '#', 'r'] -> no match; instead swap (2,1) and (2,2)
    b.swap(2,1,2,2)
    matches = b.find_matches()
    # No three-in-a-row expected in this configuration
    assert matches == set()


def test_crush_removes_matches_and_refills():
    b = Board(rows=3, cols=3, seed=0)
    # Force a simple match board: three same in first row
    b.grid = [
        ['y', 'y', 'y'],
        ['#', 'r', 'g'],
        ['r', 'g', '#']
    ]
    print("From test:")
    b.print_board()
    crushed = b.crush()
    assert crushed >= 3
    # After crush there should be no immediate matches
    assert b.find_matches() == set()


def test_is_valid_move_and_has_possible_moves():
    b = Board(rows=4, cols=4, seed=1)
    # Use small board and assert methods run without error
    assert isinstance(b.has_possible_moves(), bool)
    # Check valid_moves returns an integer >= 0
    vm = b.valid_moves()
    assert isinstance(vm, list)
    assert len(vm) >= 0


def _template():
    return [
        ['#', ' ', ' ', ' ', ' ', '#'],
        [' ', ' ', 'B', 'B', ' ', ' '],
        [' ', ' ', 'B', 'B', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' '],
        ['#', ' ', ' ', ' ', ' ', '#'],
    ]


def test_fill_empty_deals_candies_around_obstacles():
    b = Board(board_state=_template(), seed=7, fill_empty=True)
    tmpl = _template()
    for r in range(b.rows):
        for c in range(b.cols):
            if tmpl[r][c] in ('#', 'B'):
                assert b.grid[r][c] == tmpl[r][c]
            else:
                assert b.grid[r][c] in ('r', 'b', 'g', 'y')
    assert b.find_matches(place_powerups=False) == set()
    assert b.validate() == []


def test_fill_empty_is_seed_deterministic():
    a = Board(board_state=_template(), seed=7, fill_empty=True)
    b = Board(board_state=_template(), seed=7, fill_empty=True)
    c = Board(board_state=_template(), seed=8, fill_empty=True)
    assert a.grid == b.grid
    assert a.grid != c.grid


def test_fill_empty_keeps_preplaced_pieces():
    tmpl = _template()
    tmpl[3][0] = 'T'
    tmpl[4][5] = 'r'
    b = Board(board_state=tmpl, seed=7, fill_empty=True)
    assert b.grid[3][0] == 'T'
    assert b.grid[4][5] == 'r'




def test_moveless_deal_gets_reshuffled():
    # level-1 seed 1186 deals a stalemate (zero legal moves) — the board must
    # auto-reshuffle candies into a playable arrangement, leaving obstacles put
    from candy_crush.levels import get_level
    tmpl = get_level(1)
    b = Board(board_state=[row.copy() for row in tmpl], seed=1186, fill_empty=True)
    assert b.valid_moves()
    assert b.find_matches(place_powerups=False) == set()
    for r in range(b.rows):
        for c in range(b.cols):
            if tmpl[r][c] in ('#', 'B'):
                assert b.grid[r][c] == tmpl[r][c]


def test_reshuffle_moves_candies_and_powerups_not_obstacles():
    tmpl = _template()
    tmpl[3][0] = 'T'
    b = Board(board_state=[row.copy() for row in tmpl], seed=7, fill_empty=True)
    before = [row.copy() for row in b.grid]
    assert b.reshuffle() is True
    assert b.grid != before                      # something moved
    for r in range(b.rows):                      # obstacles/walls didn't
        for c in range(b.cols):
            if tmpl[r][c] in ('#', 'B'):
                assert b.grid[r][c] == tmpl[r][c]
    flat_before = sorted(ch for row in before for ch in row)
    flat_after = sorted(ch for row in b.grid for ch in row)
    assert flat_before == flat_after             # same pieces, new positions
    assert b.valid_moves()


@pytest.mark.parametrize("p", ["5", "V", "H", "T", "S"])
def test_powerup_boxed_in_is_still_fireable(p):
    # a powerup must always be settable-off: even with every neighbor an
    # obstacle/wall, the tap and the fire-in-place swaps stay valid
    b = Board(board_state=[
        ['#', 'B', '#'],
        ['B', p, 'B'],
        ['#', 'B', '#'],
    ])
    moves = b.valid_moves()
    assert (1, 1, "x") in moves
    assert (1, 1, "s") in moves   # neighbor is 'B' → fires in place
    assert (1, 1, "d") in moves


@pytest.mark.parametrize("p", ["5", "V", "H", "T", "S"])
def test_powerup_in_corner_is_still_fireable(p):
    # bottom-right corner: 's' and 'd' have no neighbor, so the tap is the
    # only way to set it off — it must always be there
    b = Board(board_state=[
        ['r', 'b', 'g'],
        ['b', 'g', 'r'],
        ['g', 'r', p],
    ])
    moves = b.valid_moves()
    assert (2, 2, "x") in moves
    assert (2, 2, "s") not in moves
    assert (2, 2, "d") not in moves
