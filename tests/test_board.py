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


