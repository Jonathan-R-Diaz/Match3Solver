import pytest
from candy_crush.board import Board


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


def test_create_electro_on_board():
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


@pytest.mark.parametrize("ch, count", [
    (' ', 8),
    ('@', 9),
    ('#', 6),
    ('$', 6),
    ('&', 6),
])
def test_electro_power(ch: str, count: int):
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
    crushed = b.activate_powerup(r1, c1, r2, c2)

    if ch == " ":
        ch = "@"
    for row in b.board:
        assert ch not in row
    assert crushed == count
    assert b.board[4][0] == ' '


def test_electro_valid_moves():
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