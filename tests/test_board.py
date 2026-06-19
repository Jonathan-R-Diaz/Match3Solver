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
    b.board = [
        ['$', '#', '&'],
        ['$', '#', '&'],
        ['#', '$', '$']
    ]
    # Swap (2,0) with (2,1) to make last row ['$', '#', '$'] -> no match; instead swap (2,1) and (2,2)
    b.swap(2,1,2,2)
    matches = b.find_matches()
    # No three-in-a-row expected in this configuration
    assert matches == set()


def test_crush_removes_matches_and_refills():
    b = Board(rows=3, cols=3, seed=0)
    # Force a simple match board: three same in first row
    b.board = [
        ['@', '@', '@'],
        ['#', '$', '&'],
        ['$', '&', '#']
    ]
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


def test_find_4_in_a_row():
    b = Board(rows=5, cols=5)
    # Create a vertical match of 4
    b.board = [
        ['#', '@', '@', '@', '@'],
        ['#', ' ', ' ', ' ', ' '],
        ['#', ' ', ' ', ' ', ' '],
        ['#', ' ', ' ', ' ', ' '],
        ['$', ' ', ' ', ' ', ' ']
    ]
    matches = b.find_matches()
    # Expecting a vertical match of 4 in the first column
    expected_matches = {(0,0), (1,0), (2,0), (3,0), (0,1), (0,2), (0,3), (0,4)}  # The 4 in a row plus the 4 in the first row
    assert matches == expected_matches


def test_find_5_in_a_row():
    b = Board(rows=6, cols=5)
    # Create a horizontal match of 5
    b.board = [
        ['#', '#', '#', '#', '#'],
        ['@', ' ', ' ', ' ', ' '],
        ['@', ' ', ' ', ' ', ' '],
        ['@', ' ', ' ', ' ', ' '],
        ['@', ' ', ' ', ' ', ' '],
        ['@', ' ', ' ', ' ', ' ']

    ]
    matches = b.find_matches()
    expected_matches = {(0,0), (0,1), (0,2), (0,3), (0,4), (1,0), (2,0), (3,0), (4,0), (5,0)}  # The 5 in a row plus the 5 in the first column
    assert matches == expected_matches


def test_create_5_powerup_board():
    b = Board(rows=5, cols=6)
    # Create a horizontal match of 5 to test power-up creation
    b.board = [
        ['@', '$', '$', '$', '$', '$'],
        ['@', ' ', ' ', ' ', ' ', ' '],
        ['@', ' ', ' ', ' ', ' ', ' '],
        ['@', ' ', ' ', ' ', ' ', ' '],
        ['@', ' ', ' ', ' ', ' ', ' ']
    ]

    b.crush(refill=False)  # This should create a power-up in the middle of the first column
    
    expected_board = [
        [' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' '],
        ['5', ' ', ' ', '5', ' ', ' ']
    ]
    assert b.board == expected_board  # Check that the power-up was created in the expected location


@pytest.mark.parametrize("ch", [' ', '@', '#', '$', '&'])
def test_5_powerup(ch: str):
    print("in test")
    if ch == ' ':
        move = (4, 0, "x")
    else:
        move = (4, 0, "w")
    b = Board(rows=5, cols=5)

    # Create a horizontal match of 5 to test power-up creation
    b.board = [
        ['@', '@', '#', '$', '&'],
        ['@', '@', '#', '$', '&'],
        ['@', '@', '#', '$', '&'],
        [ch , '@', '#', '$', '&'],
        ['5', '@', '#', '$', '&']
    ]
    r1, c1, d = move
    r2, c2 = b.get_neighbor(*move)
    b.activate_powerup(r1, c1, r2, c2)

    if ch == " ":
        ch = "@"
    for row in b.board:
        assert ch not in row
    assert b.board[4][0] == ' '


def test_5_powerup_valid_moves():
    b = Board(rows=3, cols=3, seed=0)
    # Force a simple match board: three same in first row
    b.board = [
        [' ', '@', ' '],
        ['#', '5', '&'],
        [' ', '&', ' ']
    ]
    matches = b.valid_moves()
    expected_matches = [(1,1,"x"),(1,1,"w"),(1,1,"a"),(1,1,"s"),(1,1,"d")]
    assert matches == expected_matches