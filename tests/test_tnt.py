import pytest
from candy_crush.board import Board


# --- Spawn tests ---

@pytest.mark.parametrize("start_board, move, junction", [
    # L-shape: junction at bottom-center (swap brings candy into corner)
    ([
        [' ', '$', ' '],
        [' ', '$', ' '],
        [' ', '$', '$'],
        ['$', ' ', ' '],
    ], (3, 0, 2, 0), (2, 1)),

    # L-shape: junction at bottom-right corner
    ([
        [' ', ' ', '$'],
        [' ', ' ', '$'],
        ['$', '$', ' '],
        [' ', ' ', '$'],
    ], (2, 2, 3, 2), (2, 2)),

    # T-shape: horizontal middle, vertical through center
    ([
        [' ', '$', ' '],
        ['$', '$', '$'],
        [' ', '$', ' '],
    ], (1, 0, 1, 1), (1, 1)),
],
ids=["L-bottom-center", "L-bottom-right", "T-center"])
@pytest.mark.board
def test_spawn_tnt(start_board, move, junction):
    b = Board(board_state=start_board, debug=True)
    r1, c1, r2, c2 = move
    b.swap(r1, c1, r2, c2)
    b.last_move = ((r1, c1), (r2, c2))
    b.pop()
    jr, jc = junction
    assert b.board[jr][jc] == "T"


# --- Activation tests ---

@pytest.mark.board
def test_tnt_clears_3x3():
    # T at center (1,1) of a 3x3 grid
    b = Board(board_state=[
        ['#', '#', '#'],
        ['#', 'T', '#'],
        ['#', '#', '#'],
    ])
    crushed = b.activate_powerup(1, 1, 1, 1)
    assert crushed == 8  # 8 surrounding candies (T itself is set to " " before clear_area)
    for row in b.board:
        for cell in row:
            assert cell == " "


@pytest.mark.board
def test_tnt_partial_board():
    # T at corner with radius=2 clears 5x5 area clamped to board bounds
    b = Board(board_state=[
        ['T', '#', '#', '#'],
        ['#', '#', '#', '#'],
        ['#', '#', '#', '#'],
    ])
    crushed = b.activate_powerup(0, 0, 0, 0)
    assert crushed == 8
    # Radius 2 from (0,0): rows 0-2, cols 0-2 all cleared
    for r in range(3):
        for c in range(3):
            assert b.board[r][c] == " "
    # Col 3 is 3 away — outside radius
    assert b.board[0][3] == "#"
    assert b.board[1][3] == "#"
    assert b.board[2][3] == "#"


@pytest.mark.board
def test_tnt_chains_rocket():
    # TNT at (1,1) should chain into H rocket at (1,2)
    b = Board(board_state=[
        ['#', '#', '#', '#', '#'],
        ['#', 'T', 'H', '#', '#'],
        ['#', '#', '#', '#', '#'],
    ])
    crushed = b.activate_powerup(1, 1, 1, 1)
    assert crushed == 11
    for j in range(5):
        assert b.board[1][j] == " "


@pytest.mark.board
def test_tnt_tnt_combo():
    # 11-wide board so radius=4 from col 5 leaves cols 0 and 10 untouched
    b = Board(board_state=[
        ['#'] * 11 for _ in range(11)
    ])
    b.board[4][5] = "T"
    b.board[4][6] = "T"
    crushed = b.activate_powerup(4, 5, 4, 6)
    assert crushed == 79
    # radius=4 from (4,5): rows 0-8, cols 1-9 cleared; cols 0 & 10 and rows 9-10 untouched
    for r in range(9):
        for c in range(1, 10):
            assert b.board[r][c] == " ", f"Expected empty at ({r},{c})"
    for r in range(11):
        assert b.board[r][0] == "#"
        assert b.board[r][10] == "#"
    for c in range(11):
        assert b.board[9][c] == "#"
        assert b.board[10][c] == "#"


@pytest.mark.board
def test_tnt_valid_moves():
    b = Board(board_state=[
        [' ', '@', ' '],
        ['#', 'T', '&'],
        [' ', '&', ' '],
    ])
    moves = b.valid_moves()
    assert (1, 1, "x") in moves
    assert (1, 1, "w") in moves
    assert (1, 1, "a") in moves
    assert (1, 1, "s") in moves
    assert (1, 1, "d") in moves
