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


@pytest.mark.board
def test_cross_with_four_run_spawns_tnt_not_rocket():
    # Vertical 4-run (col 2) crossing a horizontal 3-run (row 1):
    # TNT has priority — one T at the junction, no rocket anywhere.
    b = Board(board_state=[
        ['g', 'b', 'r', 'y'],
        ['r', 'r', 'r', 'g'],
        ['b', 'g', 'r', 'b'],
        ['y', 'b', 'r', 'g'],
    ])
    b.find_matches()
    assert b.board[1][2] == 'T'
    flat = [cell for row in b.board for cell in row]
    assert 'V' not in flat and 'H' not in flat


@pytest.mark.board
def test_cross_of_two_four_runs_spawns_single_tnt():
    # 4-run down col 1 crossing a 4-run across row 1 → one TNT, zero rockets
    b = Board(board_state=[
        ['g', 'r', 'b', 'y', 'g'],
        ['r', 'r', 'r', 'r', 'b'],
        ['b', 'r', 'g', 'b', 'y'],
        ['y', 'r', 'b', 'g', 'r'],
    ])
    b.find_matches()
    assert b.board[1][1] == 'T'
    flat = [cell for row in b.board for cell in row]
    assert 'V' not in flat and 'H' not in flat


@pytest.mark.board
def test_plain_four_run_still_spawns_rocket():
    # No crossing line — the 4-run must still produce a rocket, not a TNT
    b = Board(board_state=[
        ['r', 'r', 'r', 'r'],
        ['g', 'b', 'y', 'g'],
        ['b', 'g', 'b', 'y'],
    ])
    b.find_matches()
    flat = [cell for row in b.board for cell in row]
    assert 'T' not in flat
    assert ('V' in flat) or ('H' in flat)


@pytest.mark.gameplay
def test_tnt_swap_creating_tnt_fires_old_and_keeps_new():
    from candy_crush.game import Game
    # Selecting the T at (3,2) and swiping down swaps it with the 'b' at (4,2).
    # The 'b' lands at (3,2), completing col-2 and row-3 runs → new TNT at (3,2).
    # The old TNT must fire from (4,2) immediately, sparing the new TNT.
    g = Game(board_state=[
        ['g', 'r', 'y', 'g'],
        ['r', 'g', 'b', 'y'],
        ['y', 'r', 'b', 'g'],
        ['b', 'b', 'T', 'r'],
        ['r', 'g', 'b', 'g'],
    ])
    _, reward, _, _ = g.step((3, 2, 's'))
    assert reward > 0
    # the new TNT survived the old one's blast (it may have dropped a row)
    assert any(cell == 'T' for row in g.board.board for cell in row)


@pytest.mark.board
def test_tnt_blast_chains_spinner():
    # S at (0,1) is inside the TNT's radius-2 blast: it must FIRE (clearing its
    # own cardinal neighbors), not just be deleted like a plain candy.
    # (3,4) is outside the blast but cardinal to nothing... proof cell:
    # the spinner at (0,1) pops one random obstacle; the lone B at (4,4) is
    # outside the TNT blast (radius 2 from (2,1) covers rows 0-4, cols 0-3),
    # so only a chained spinner can remove it.
    b = Board(board_state=[
        ['r', 'S', 'g', 'y', 'b'],
        ['g', 'b', 'r', 'g', 'y'],
        ['y', 'T', 'b', 'r', 'g'],
        ['b', 'g', 'y', 'b', 'r'],
        ['r', 'y', 'g', 'r', 'B'],
    ])
    b.activate_powerup(2, 1, 2, 1)
    assert b.board[4][4] == ' '   # box popped → spinner chained, not deleted


# --- Activation tests ---

@pytest.mark.board
def test_tnt_clears_3x3():
    # T at center (1,1) of a 3x3 grid
    b = Board(board_state=[
        ['$', '$', '$'],
        ['$', 'T', '$'],
        ['$', '$', '$'],
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
        ['T', '$', '$', '$'],
        ['$', '$', '$', '$'],
        ['$', '$', '$', '$'],
    ])
    crushed = b.activate_powerup(0, 0, 0, 0)
    assert crushed == 8
    assert b.board == [
        [' ', ' ', ' ', '$'],
        [' ', ' ', ' ', '$'],
        [' ', ' ', ' ', '$'],
    ]


@pytest.mark.board
def test_tnt_chains_rocket():
    # TNT at (1,1) blast hits H at (1,2); rocket clears all of row 1; col 4 outside TNT radius
    b = Board(board_state=[
        ['$', '$', '$', '$', '$'],
        ['$', 'T', 'H', '$', '$'],
        ['$', '$', '$', '$', '$'],
    ])
    crushed = b.activate_powerup(1, 1, 1, 1)
    assert crushed == 11
    assert b.board == [
        [' ', ' ', ' ', ' ', '$'],
        [' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', '$'],
    ]


@pytest.mark.board
def test_tnt_chains_tnt():
    # T at (3,2) blast hits T at (3,4) (exactly at radius edge); second TNT fires its own blast.
    # First blast: rows 1-5 cols 0-4. Second blast: rows 1-5 cols 2-6. Union clears rows 1-5 entirely.
    b = Board(board_state=[['$'] * 7 for _ in range(7)])
    b.board[3][2] = 'T'
    b.board[3][4] = 'T'
    crushed = b.activate_powerup(3, 2, 3, 2)
    assert crushed == 33
    assert b.board == [
        ['$', '$', '$', '$', '$', '$', '$'],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
        ['$', '$', '$', '$', '$', '$', '$'],
    ]


@pytest.mark.board
def test_tnt_valid_moves():
    b = Board(board_state=[
        [' ', '@', ' '],
        ['$', 'T', '&'],
        [' ', '&', ' '],
    ])
    moves = b.valid_moves()
    assert (1, 1, "x") in moves
    assert (1, 1, "w") in moves
    assert (1, 1, "a") in moves
    assert (1, 1, "s") in moves
    assert (1, 1, "d") in moves
