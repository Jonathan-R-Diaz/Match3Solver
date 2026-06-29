import pytest
from candy_crush.board import Board


@pytest.mark.board
def test_rocket_rocket_combo():
    # H at (2,1) + V at (2,2): + fires from (2,2), clearing row 2 and col 2
    b = Board(board_state=[
        ['#', '#', '#', '#', '#'],
        ['#', '#', '#', '#', '#'],
        ['#', 'H', 'V', '#', '#'],
        ['#', '#', '#', '#', '#'],
        ['#', '#', '#', '#', '#'],
    ])
    crushed = b.activate_powerup(2, 1, 2, 2)
    assert crushed == 7
    assert b.board == [
        ['#', '#', ' ', '#', '#'],
        ['#', '#', ' ', '#', '#'],
        [' ', ' ', ' ', ' ', ' '],
        ['#', '#', ' ', '#', '#'],
        ['#', '#', ' ', '#', '#'],
    ]


@pytest.mark.board
def test_tnt_tnt_combo():
    # Two adjacent TNTs at (4,5)+(4,6): radius=4 blast from (4,5)
    # Clears rows 0-8, cols 1-9; col 0, col 10, and rows 9-10 survive
    b = Board(board_state=[['#'] * 11 for _ in range(11)])
    b.board[4][5] = 'T'
    b.board[4][6] = 'T'
    crushed = b.activate_powerup(4, 5, 4, 6)
    assert crushed == 79
    assert b.board == [
        ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'],
        ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'],
        ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'],
        ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'],
        ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'],
        ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'],
        ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'],
        ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'],
        ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'],
        ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#'],
        ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#'],
    ]


@pytest.mark.board
def test_eb_eb_combo():
    # 15x15 board: '#' everywhere except two adjacent '5' at center
    # EB+EB sweeps the entire board: all 223 '#' cells cleared directly
    board = [['#'] * 15 for _ in range(15)]
    board[7][7] = '5'
    board[7][8] = '5'
    b = Board(board_state=board)
    crushed = b.activate_powerup(7, 7, 7, 8)
    assert crushed == 223
    assert b.board == [[' '] * 15 for _ in range(15)]


@pytest.mark.board
def test_eb_tnt_combo():
    # 15x15 board: '@' everywhere (most common), '#' at 4 corners, '5'+'T' at center
    # EB+TNT replaces all 219 '@' with T and fires each; 4 corner '#' cells get caught
    board = [['@'] * 15 for _ in range(15)]
    board[0][0] = '#'
    board[0][14] = '#'
    board[14][0] = '#'
    board[14][14] = '#'
    board[7][7] = '5'
    board[7][8] = 'T'
    b = Board(board_state=board)
    crushed = b.activate_powerup(7, 7, 7, 8)
    assert crushed == 4
    assert b.board == [[' '] * 15 for _ in range(15)]


@pytest.mark.board
def test_eb_rocket_combo():
    # 15x15 board: '@' everywhere (most common), '#' at 4 corners, '5'+'H' at center
    # EB+Rocket replaces all 219 '@' with H and fires each; every row gets cleared,
    # catching the 4 corner '#' cells
    board = [['@'] * 15 for _ in range(15)]
    board[0][0] = '#'
    board[0][14] = '#'
    board[14][0] = '#'
    board[14][14] = '#'
    board[7][7] = '5'
    board[7][8] = 'H'
    b = Board(board_state=board)
    crushed = b.activate_powerup(7, 7, 7, 8)
    assert crushed == 4
    assert b.board == [[' '] * 15 for _ in range(15)]
