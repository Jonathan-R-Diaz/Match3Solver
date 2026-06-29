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
    assert crushed == 8
    assert b.board == [
        [' ', ' ', ' '],
        [' ', ' ', ' '],
        [' ', ' ', ' '],
    ]


@pytest.mark.board
def test_tnt_partial_board():
    # T at corner: radius=2 blast clamped to board bounds; col 3 is 3 away — outside radius
    b = Board(board_state=[
        ['T', '#', '#', '#'],
        ['#', '#', '#', '#'],
        ['#', '#', '#', '#'],
    ])
    crushed = b.activate_powerup(0, 0, 0, 0)
    assert crushed == 8
    assert b.board == [
        [' ', ' ', ' ', '#'],
        [' ', ' ', ' ', '#'],
        [' ', ' ', ' ', '#'],
    ]


@pytest.mark.board
def test_tnt_chains_rocket():
    # TNT at (1,1) blast hits H at (1,2); rocket clears all of row 1; col 4 outside TNT radius
    b = Board(board_state=[
        ['#', '#', '#', '#', '#'],
        ['#', 'T', 'H', '#', '#'],
        ['#', '#', '#', '#', '#'],
    ])
    crushed = b.activate_powerup(1, 1, 1, 1)
    assert crushed == 11
    assert b.board == [
        [' ', ' ', ' ', ' ', '#'],
        [' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', '#'],
    ]


@pytest.mark.board
def test_tnt_chains_tnt():
    # T at (3,2) blast hits T at (3,4) (exactly at radius edge); second TNT fires its own blast.
    # First blast: rows 1-5 cols 0-4. Second blast: rows 1-5 cols 2-6. Union clears rows 1-5 entirely.
    b = Board(board_state=[['#'] * 7 for _ in range(7)])
    b.board[3][2] = 'T'
    b.board[3][4] = 'T'
    crushed = b.activate_powerup(3, 2, 3, 2)
    assert crushed == 33
    assert b.board == [
        ['#', '#', '#', '#', '#', '#', '#'],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
        ['#', '#', '#', '#', '#', '#', '#'],
    ]


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
