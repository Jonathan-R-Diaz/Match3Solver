import pytest
from candy_crush.board import Board


@pytest.mark.board
def test_rocket_rocket_combo():
    # H at (2,1) + V at (2,2): + fires from (2,2), clearing row 2 and col 2
    b = Board(board_state=[
        ['$', '$', '$', '$', '$'],
        ['$', '$', '$', '$', '$'],
        ['$', 'H', 'V', '$', '$'],
        ['$', '$', '$', '$', '$'],
        ['$', '$', '$', '$', '$'],
    ])
    crushed = b.activate_powerup(2, 1, 2, 2)
    assert crushed == 7
    assert b.board == [
        ['$', '$', ' ', '$', '$'],
        ['$', '$', ' ', '$', '$'],
        [' ', ' ', ' ', ' ', ' '],
        ['$', '$', ' ', '$', '$'],
        ['$', '$', ' ', '$', '$'],
    ]


@pytest.mark.board
def test_tnt_tnt_combo():
    # Two adjacent TNTs at (4,5)+(4,6): radius=4 blast from (4,5)
    # Clears rows 0-8, cols 1-9; col 0, col 10, and rows 9-10 survive
    b = Board(board_state=[['$'] * 11 for _ in range(11)])
    b.board[4][5] = 'T'
    b.board[4][6] = 'T'
    crushed = b.activate_powerup(4, 5, 4, 6)
    assert crushed == 79
    assert b.board == [
        ['$', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '$'],
        ['$', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '$'],
        ['$', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '$'],
        ['$', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '$'],
        ['$', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '$'],
        ['$', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '$'],
        ['$', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '$'],
        ['$', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '$'],
        ['$', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '$'],
        ['$', '$', '$', '$', '$', '$', '$', '$', '$', '$', '$'],
        ['$', '$', '$', '$', '$', '$', '$', '$', '$', '$', '$'],
    ]


@pytest.mark.board
def test_rocket_tnt_combo():
    # H at (3,3) + T at (3,4): fires 3 rows (2-4) + 3 cols (3-5) centered on (3,4)
    b = Board(board_state=[['$'] * 7 for _ in range(7)])
    b.board[3][3] = 'H'
    b.board[3][4] = 'T'
    crushed = b.activate_powerup(3, 3, 3, 4)
    assert crushed == 31
    assert b.board == [
        ['$', '$', '$', ' ', ' ', ' ', '$'],
        ['$', '$', '$', ' ', ' ', ' ', '$'],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
        ['$', '$', '$', ' ', ' ', ' ', '$'],
        ['$', '$', '$', ' ', ' ', ' ', '$'],
    ]


@pytest.mark.board
def test_rocket_tnt_chain():
    # H rocket sweeps row 1, hits T at (1,3); TNT blasts rows 0-3 cols 1-5
    # col 0 and col 6 outside TNT radius; row 4 outside TNT radius
    b = Board(board_state=[
        ['$', '$', '$', '$', '$', '$', '$'],
        ['H', '$', '$', 'T', '$', '$', '$'],
        ['$', '$', '$', '$', '$', '$', '$'],
        ['$', '$', '$', '$', '$', '$', '$'],
        ['$', '$', '$', '$', '$', '$', '$'],
    ])
    crushed = b.activate_powerup(1, 0, 1, 0)
    assert crushed == 20
    assert b.board == [
        ['$', ' ', ' ', ' ', ' ', ' ', '$'],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
        ['$', ' ', ' ', ' ', ' ', ' ', '$'],
        ['$', ' ', ' ', ' ', ' ', ' ', '$'],
        ['$', '$', '$', '$', '$', '$', '$'],
    ]


@pytest.mark.board
def test_eb_eb_combo():
    # 15x15 board: '$' everywhere except two adjacent '5' at center
    # EB+EB sweeps the entire board: all 223 '$' cells cleared directly
    board = [['$'] * 15 for _ in range(15)]
    board[7][7] = '5'
    board[7][8] = '5'
    b = Board(board_state=board)
    crushed = b.activate_powerup(7, 7, 7, 8)
    assert crushed == 223
    assert b.board == [[' '] * 15 for _ in range(15)]


@pytest.mark.board
def test_eb_tnt_combo():
    # 15x15 board: '@' everywhere (most common), '$' at 4 corners, '5'+'T' at center
    # EB+TNT replaces all 219 '@' with T and fires each; 4 corner '$' cells get caught
    board = [['@'] * 15 for _ in range(15)]
    board[0][0] = '$'
    board[0][14] = '$'
    board[14][0] = '$'
    board[14][14] = '$'
    board[7][7] = '5'
    board[7][8] = 'T'
    b = Board(board_state=board)
    crushed = b.activate_powerup(7, 7, 7, 8)
    assert crushed == 4
    assert b.board == [[' '] * 15 for _ in range(15)]


@pytest.mark.board
def test_eb_rocket_combo():
    # 15x15 board: '@' everywhere (most common), '$' at 4 corners, '5'+'H' at center
    # EB+Rocket replaces all 219 '@' with H and fires each; every row gets cleared,
    # catching the 4 corner '$' cells
    board = [['@'] * 15 for _ in range(15)]
    board[0][0] = '$'
    board[0][14] = '$'
    board[14][0] = '$'
    board[14][14] = '$'
    board[7][7] = '5'
    board[7][8] = 'H'
    b = Board(board_state=board)
    crushed = b.activate_powerup(7, 7, 7, 8)
    assert crushed == 4
    assert b.board == [[' '] * 15 for _ in range(15)]


# ── EB + Spinner combo ────────────────────────────────────────────────────────

@pytest.mark.board
def test_eb_spinner_replaces_most_common_candy_with_spinners():
    # 'r' appears 6 times, others 1 each → all 'r' become 'S' and fire
    b = Board(board_state=[
        ['r', 'r', 'r'],
        ['r', '5', 'b'],
        ['r', 'g', 'S'],
    ])
    b.activate_powerup(1, 1, 2, 2)
    assert all(b.board[r][c] != 'r' for r in range(3) for c in range(3))


@pytest.mark.board
def test_eb_spinner_fires_each_replacement():
    # 3×3 board: 'r' is most common (4 cells). Each replacement spinner fires,
    # clearing its cardinal neighbors. Net result: no 'r' and high crushed count.
    b = Board(board_state=[
        ['r', 'b', 'r'],
        ['g', '5', 'b'],
        ['r', 'g', 'S'],
    ])
    crushed = b.activate_powerup(1, 1, 2, 2)
    assert crushed > 0
    assert all(b.board[r][c] != 'r' for r in range(3) for c in range(3))


@pytest.mark.board
def test_eb_spinner_order_does_not_matter():
    # Spinner on left, EB on right — same outcome as EB left, Spinner right
    b1 = Board(board_state=[
        ['r', 'r', 'g'],
        ['S', '5', 'b'],
        ['r', 'g', 'b'],
    ])
    b2 = Board(board_state=[
        ['r', 'r', 'g'],
        ['S', '5', 'b'],
        ['r', 'g', 'b'],
    ])
    c1 = b1.activate_powerup(1, 0, 1, 1)   # Spinner first
    c2 = b2.activate_powerup(1, 1, 1, 0)   # EB first
    assert c1 == c2


@pytest.mark.board
def test_eb_spinner_does_not_chain_adjacent_powerups():
    # 'r' is most common (6 cells, entire row 0).
    # Spinners replace all of row 0 and each fires south into row 1.
    # Spinner at (0,2) hits V at (1,2) — with chain=False V is skipped entirely.
    # Proof: (2,2) is in V's column but unreachable by any row-0 spinner.
    #        If V had fired it would be ' '; since it was skipped it stays 'g'.
    b = Board(board_state=[
        ['r', 'r', 'r', 'r', 'r', 'r'],
        ['b', 'b', 'V', 'b', 'b', 'b'],
        ['g', 'g', 'g', 'g', '5', 'S'],
    ])
    b.activate_powerup(2, 4, 2, 5)
    assert b.board[1][2] == 'V'   # V was skipped entirely — still on the board
    assert b.board[2][2] == 'g'   # V's column was NOT cleared (V never fired)


@pytest.mark.board
def test_eb_spinner_clears_eb_and_spinner_cells():
    b = Board(board_state=[
        ['r', 'b', 'r'],
        ['b', '5', 'S'],
        ['r', 'b', 'r'],
    ])
    b.activate_powerup(1, 1, 1, 2)
    assert b.board[1][1] == ' '
    assert b.board[1][2] == ' '


# ── Spinner + Spinner combo ───────────────────────────────────────────────────

@pytest.mark.board
def test_spinner_spinner_fires_both_spinners():
    # S at (0,0) and (0,2). Both spinner cells must be cleared after the combo.
    b = Board(board_state=[
        ['S', 'r', 'S'],
        ['g', 'b', 'g'],
        ['r', 'r', 'r'],
    ])
    b.activate_powerup(0, 0, 0, 2)
    assert b.board[0][0] == ' '
    assert b.board[0][2] == ' '


@pytest.mark.board
def test_spinner_spinner_extra_pops_one_obstacle():
    # Both spinners surrounded by empty → 0 cardinals cleared.
    # Each spinner does 1 random box pop (2 total), plus the extra pop = 3 total.
    b = Board(board_state=[
        [' ', 'S', ' '],
        [' ', 'S', ' '],
        [' ', ' ', ' '],
        ['B', 'B', 'B'],
    ])
    before = sum(cell == 'B' for row in b.board for cell in row)
    b.activate_powerup(0, 1, 1, 1)
    assert sum(cell == 'B' for row in b.board for cell in row) == before - 3


@pytest.mark.board
def test_spinner_spinner_chains_adjacent_powerup():
    # Unlike EB+Spinner, Spinner+Spinner DOES chain into adjacent powerups.
    b = Board(board_state=[
        ['S', 'H', 'S'],
        ['g', 'b', 'g'],
        ['r', 'r', 'r'],
    ])
    b.activate_powerup(0, 0, 0, 2)
    assert b.board[0][1] == ' '


@pytest.mark.board
def test_spinner_spinner_order_does_not_matter():
    b1 = Board(board_state=[
        ['r', 'g', 'b'],
        ['S', 'r', 'S'],
        ['b', 'g', 'r'],
    ])
    b2 = Board(board_state=[
        ['r', 'g', 'b'],
        ['S', 'r', 'S'],
        ['b', 'g', 'r'],
    ])
    c1 = b1.activate_powerup(1, 0, 1, 2)
    c2 = b2.activate_powerup(1, 2, 1, 0)
    assert c1 == c2


@pytest.mark.board
def test_spinner_spinner_combo():
    b = Board(board_state=[
        [' ', 'S', ' '],
        [' ', 'S', ' '],
        [' ', ' ', ' '],
        ['B', 'B', 'B'],
    ])
    b.activate_powerup(0, 1, 1, 1)
    assert sum(cell == 'B' for row in b.board for cell in row) == 0
