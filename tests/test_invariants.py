import pytest
from engine.board import Board
from engine.game import Game


@pytest.mark.board
def test_validate_healthy_board():
    b = Board(rows=6, cols=6, seed=3)
    assert b.validate() == []


@pytest.mark.board
def test_validate_flags_unknown_symbol():
    b = Board(board_state=[
        ['r', 'Z'],
        ['g', 'b'],
    ])
    assert any('unknown symbol' in v for v in b.validate())


@pytest.mark.board
def test_validate_flags_floating_piece():
    b = Board(board_state=[
        ['r', 'b'],
        [' ', 'g'],
        ['y', 'r'],
    ])
    assert any('floating' in v for v in b.validate())


@pytest.mark.board
def test_validate_piece_resting_on_wall_or_box_is_fine():
    b = Board(board_state=[
        ['r', 'b'],
        ['#', 'B'],
        [' ', ' '],
    ])
    violations = b.validate()
    assert not any('floating' in v for v in violations)


@pytest.mark.board
def test_validate_flags_unresolved_matches():
    b = Board(board_state=[
        ['r', 'r', 'r'],
        ['g', 'b', 'g'],
        ['b', 'g', 'b'],
    ])
    assert any('unresolved matches' in v for v in b.validate())


@pytest.mark.gameplay
def test_debug_game_step_passes_validation():
    g = Game(rows=6, cols=6, seed=4, debug=True)
    moves = [m for m in g.board.valid_moves() if m[2] != 'x']
    assert moves
    g.step(moves[0])   # raises AssertionError if invariants break
