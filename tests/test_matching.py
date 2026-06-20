import pytest
from candy_crush.board import Board


@pytest.mark.parametrize("single_row, expected_matches", 
    [
        ([['#', '#', "#", '_', '_']], {(0,0), (0,1), (0,2)}),
        ([['_', '#', '#', "#", '_']], {(0,1), (0,2), (0,3)}),
        ([['_', '_', '#', '#', "#"]], {(0,2), (0,3), (0,4)})
    ],
    ids=["left", "center", "right"])
def test_matches_3_horizontal(single_row, expected_matches):
    b = Board(board_state=single_row)
    matches = b.find_matches()
    assert matches == expected_matches


@pytest.mark.parametrize("single_row, expected_matches", 
    [
        ([['#', '#', '#', "#", '_', '_']], {(0,0), (0,1), (0,2), (0,3)}),
        ([['_', '#', '#', '#', "#", '_']], {(0,1), (0,2), (0,3), (0,4)}),
        ([['_', '_', '#', '#', '#', "#"]], {(0,2), (0,3), (0,4), (0,5)})
    ],
    ids=["left", "center", "right"])
def test_matches_4_horizontal(single_row, expected_matches):
    b = Board(board_state=single_row)
    matches = b.find_matches()
    assert matches == expected_matches


@pytest.mark.parametrize("single_row, expected_matches", 
    [
        ([['#', '#', '#', "#", '#', '_', '_']], {(0,0), (0,1), (0,2), (0,3), (0,4)}),
        ([['_', '#', '#', '#', "#", '#', '_']], {(0,1), (0,2), (0,3), (0,4), (0,5)}),
        ([['_', '_', '#', '#', '#', "#", '#']], {(0,2), (0,3), (0,4), (0,5), (0,6)})
    ],
    ids=["left", "center", "right"])
def test_matches_5_horizontal(single_row, expected_matches):
    b = Board(board_state=single_row)
    matches = b.find_matches()
    assert matches == expected_matches


@pytest.mark.parametrize("single_col, expected_matches", 
    [
        ([['#'], ['#'], ['#'], ['_'], ['_']], {(0,0), (1,0), (2,0)}),
        ([['_'], ['#'], ['#'], ['#'], ['_']], {(1,0), (2,0), (3,0)}),
        ([['_'], ['_'], ['#'], ['#'], ['#']], {(2,0), (3,0), (4,0)})
    ],
    ids=["upper", "center", "lower"])
def test_matches_3_vertical(single_col, expected_matches):
    b = Board(board_state=single_col)
    matches = b.find_matches()
    assert matches == expected_matches


@pytest.mark.parametrize("single_col, expected_matches", 
    [
        ([['#'], ['#'], ['#'], ['#'], ['_'], ['_']], {(0,0), (1,0), (2,0), (3,0)}),
        ([['_'], ['#'], ['#'], ['#'], ['#'], ['_']], {(1,0), (2,0), (3,0), (4,0)}),
        ([['_'], ['_'], ['#'], ['#'], ['#'], ['#']], {(2,0), (3,0), (4,0), (5,0)})
    ],
    ids=["upper", "center", "lower"])
def test_matches_4_vertical(single_col, expected_matches):
    b = Board(board_state=single_col)
    matches = b.find_matches()
    assert matches == expected_matches


@pytest.mark.parametrize("single_col, expected_matches", 
    [
        ([['#'], ['#'], ['#'], ['#'], ['#'], ['_'], ['_']], {(0,0), (1,0), (2,0), (3,0), (4,0)}),
        ([['_'], ['#'], ['#'], ['#'], ['#'], ['#'], ['_']], {(1,0), (2,0), (3,0), (4,0), (5,0)}),
        ([['_'], ['_'], ['#'], ['#'], ['#'], ['#'], ['#']], {(2,0), (3,0), (4,0), (5,0), (6,0)})
    ],
    ids=["upper", "center", "lower"])
def test_matches_5_vertical(single_col, expected_matches):
    b = Board(board_state=single_col)
    matches = b.find_matches()
    assert matches == expected_matches
