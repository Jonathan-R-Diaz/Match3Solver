import pytest
from candy_crush.board import Board
from candy_crush.game import Game


# ── helpers ──────────────────────────────────────────────────────────────────

def box_count(board_obj):
    return sum(cell == 'B' for row in board_obj.board for cell in row)

def fire(board_obj, r, c):
    return board_obj.activate_powerup(r, c, r, c)


# ── basic mechanics ───────────────────────────────────────────────────────────

@pytest.mark.board
def test_spinner_clears_four_cardinal_neighbors():
    b = Board(board_state=[
        [' ', 'r', ' '],
        ['g', 'S', 'y'],
        [' ', 'b', ' '],
    ])
    crushed = fire(b, 1, 1)
    assert crushed == 4
    assert b.board[0][1] == ' '
    assert b.board[1][0] == ' '
    assert b.board[1][2] == ' '
    assert b.board[2][1] == ' '
    assert b.board[1][1] == ' '   # spinner itself gone


@pytest.mark.board
def test_spinner_does_not_clear_diagonals():
    b = Board(board_state=[
        ['r', ' ', 'r'],
        [' ', 'S', ' '],
        ['r', ' ', 'r'],
    ])
    fire(b, 1, 1)
    # corners must survive
    assert b.board[0][0] == 'r'
    assert b.board[0][2] == 'r'
    assert b.board[2][0] == 'r'
    assert b.board[2][2] == 'r'


@pytest.mark.board
def test_spinner_at_top_edge():
    # N=out of bounds, S=(1,1)='b', W=(0,0)='r', E=(0,2)='r' → 3 cells
    b = Board(board_state=[
        ['r', 'S', 'r'],
        ['g', 'b', 'y'],
    ])
    crushed = fire(b, 0, 1)
    assert crushed == 3
    assert b.board[0][0] == ' '
    assert b.board[0][2] == ' '
    assert b.board[1][1] == ' '


@pytest.mark.board
def test_spinner_at_corner():
    b = Board(board_state=[
        ['S', 'r'],
        ['g', 'b'],
    ])
    crushed = fire(b, 0, 0)
    assert crushed == 2    # only E and S neighbors
    assert b.board[0][1] == ' '
    assert b.board[1][0] == ' '
    assert b.board[1][1] == 'b'   # diagonal, untouched


@pytest.mark.board
def test_spinner_skips_walls():
    b = Board(board_state=[
        [' ', '#', ' '],
        ['#', 'S', '#'],
        [' ', '#', ' '],
    ])
    crushed = fire(b, 1, 1)
    assert crushed == 0
    # all walls intact
    assert b.board[0][1] == '#'
    assert b.board[1][0] == '#'
    assert b.board[1][2] == '#'
    assert b.board[2][1] == '#'


@pytest.mark.board
def test_spinner_skips_empty_neighbors():
    b = Board(board_state=[
        [' ', ' ', ' '],
        [' ', 'S', ' '],
        [' ', ' ', ' '],
    ])
    crushed = fire(b, 1, 1)
    assert crushed == 0


# ── obstacle interaction ─────────────────────────────────────────────────────

@pytest.mark.board
def test_spinner_pops_exactly_one_obstacle_when_present():
    # Boxes in row 3 — none are cardinal neighbours of spinner at (1,1)
    b = Board(board_state=[
        [' ', ' ', ' '],
        [' ', 'S', ' '],
        [' ', ' ', ' '],
        ['B', 'B', 'B'],
    ])
    before = box_count(b)
    fire(b, 1, 1)
    assert box_count(b) == before - 1


@pytest.mark.board
def test_spinner_pops_no_obstacle_when_none_present():
    b = Board(board_state=[
        [' ', 'r', ' '],
        ['g', 'S', 'y'],
        [' ', 'b', ' '],
    ])
    before = box_count(b)
    fire(b, 1, 1)
    assert box_count(b) == before   # still 0


@pytest.mark.board
def test_spinner_adjacent_box_counts_as_cardinal_clear_not_obstacle_pop():
    # B north of spinner cleared as a cardinal hit;
    # random pop then removes one more from the non-adjacent row below
    b = Board(board_state=[
        [' ', 'B', ' '],   # B north — cardinal neighbour
        [' ', 'S', ' '],
        [' ', ' ', ' '],   # empty row so south cardinal is empty
        ['B', 'B', 'B'],   # boxes not adjacent to spinner
    ])
    before = box_count(b)
    fire(b, 1, 1)
    # 1 adjacent B (north) + 1 random obstacle pop = 2 boxes removed
    assert box_count(b) == before - 2


@pytest.mark.board
def test_spinner_crushed_count_with_one_obstacle():
    b = Board(board_state=[
        [' ', 'r', ' '],
        ['g', 'S', 'y'],
        [' ', 'b', ' '],
        ['B', ' ', ' '],
    ])
    crushed = fire(b, 1, 1)
    assert crushed == 5   # 4 cardinal candies + 1 obstacle


# ── powerup chaining ──────────────────────────────────────────────────────────

@pytest.mark.board
def test_spinner_chains_adjacent_rocket():
    # H rocket north of spinner: cardinal clear fires it, clearing its row
    b = Board(board_state=[
        ['r', 'H', 'r'],
        ['g', 'S', 'y'],
        ['r', 'r', 'r'],
    ])
    fire(b, 1, 1)
    # H was at (0,1); when spinner hits it, H fires and clears row 0
    assert b.board[0][0] == ' '
    assert b.board[0][2] == ' '


@pytest.mark.board
def test_spinner_chains_adjacent_tnt():
    b = Board(board_state=[
        [' ', 'T', ' '],
        [' ', 'S', ' '],
        [' ', ' ', ' '],
    ])
    fire(b, 1, 1)
    # T at (0,1) fires with radius 2; should clear the surrounding area
    assert b.board[0][1] == ' '


# ── swap mechanics ────────────────────────────────────────────────────────────

@pytest.mark.board
def test_swap_candy_into_spinner_fires_from_candy_position():
    # Candy at (1,1), spinner at (1,2). Swap moves spinner to (1,1).
    # Spinner must fire from (1,1), clearing (0,1), (2,1), (1,0), (1,2).
    b = Board(board_state=[
        ['r', 'g', 'r'],
        ['b', 'r', 'S'],
        ['r', 'g', 'r'],
    ])
    b.swap(1, 1, 1, 2)               # candy slides right, spinner to (1,1)
    assert b.board[1][1] == 'S'      # confirm spinner is now at (1,1)
    fire(b, 1, 1)
    assert b.board[0][1] == ' '      # north of (1,1)
    assert b.board[2][1] == ' '      # south of (1,1)
    assert b.board[1][0] == ' '      # west of (1,1)
    assert b.board[1][2] == ' '      # east of (1,1) — the candy that slid there
    assert b.board[1][1] == ' '      # spinner itself gone


@pytest.mark.board
def test_select_spinner_directly_fires_from_its_own_position():
    # Spinner at (0,0). Firing directly: only E=(0,1) and S=(1,0) are in-bounds.
    b = Board(board_state=[
        ['S', 'r', 'r'],
        ['g', 'b', 'g'],
        ['r', 'r', 'b'],
    ])
    fire(b, 0, 0)
    assert b.board[0][0] == ' '      # spinner itself gone
    assert b.board[0][1] == ' '      # east
    assert b.board[1][0] == ' '      # south
    assert b.board[1][1] == 'b'      # diagonal — untouched


# ── integration ───────────────────────────────────────────────────────────────

@pytest.mark.gameplay
def test_spinner_appears_in_valid_moves():
    g = Game(board_state=[
        ['r', 'g', 'r'],
        ['g', 'S', 'g'],
        ['r', 'g', 'r'],
    ])
    moves = g.board.valid_moves()
    spinner_moves = [(r, c, d) for r, c, d in moves if r == 1 and c == 1]
    assert len(spinner_moves) > 0


@pytest.mark.gameplay
def test_spinner_step_via_game():
    g = Game(board_state=[
        ['r', 'g', 'r'],
        ['g', 'S', 'g'],
        ['r', 'g', 'r'],
        ['B', 'B', 'B'],
    ])
    before = box_count(g.board)
    _, reward, _, _ = g.step((1, 1, 'x'))
    assert reward > 0
    assert box_count(g.board) < before
