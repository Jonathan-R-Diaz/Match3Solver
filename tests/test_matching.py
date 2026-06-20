import pytest
from candy_crush.board import Board


@pytest.mark.parametrize("row, expected_matches", 
    [
        (['#', '#', "#", ' ', ' '], {(0,0), (0,1), (0,2)}),
        ([' ', '#', '#', "#", ' '], {(0,1), (0,2), (0,3)}),
        ([' ', ' ', '#', '#', "#"], {(0,2), (0,3), (0,4)})
    ],
    ids=["left", "center", "right"])
def test_matches_3_horizontal(row, expected_matches):
    b = Board(rows=1, cols=5)
    # Create a vertical match of 4
    b.board = [
        row,
    ]
    matches = b.find_matches()
    # Expecting a vertical match of 4 in the first column
    assert matches == expected_matches


@pytest.mark.parametrize("row, expected_matches", 
    [
        (['#', '#', '#', "#", ' ', ' '], {(0,0), (0,1), (0,2), (0,3)}),
        ([' ', '#', '#', '#', "#", ' '], {(0,1), (0,2), (0,3), (0,4)}),
        ([' ', ' ', '#', '#', '#', "#"], {(0,2), (0,3), (0,4), (0,5)})
    ],
    ids=["left", "center", "right"])
def test_matches_4_horizontal(row, expected_matches):
    b = Board(rows=1, cols=6)
    # Create a vertical match of 4
    b.board = [
        row,
    ]
    matches = b.find_matches()
    # Expecting a vertical match of 4 in the first column
    assert matches == expected_matches


@pytest.mark.parametrize("row, expected_matches", 
    [
        (['#', '#', '#', "#", '#', ' ', ' '], {(0,0), (0,1), (0,2), (0,3), (0,4)}),
        ([' ', '#', '#', '#', "#", '#', ' '], {(0,1), (0,2), (0,3), (0,4), (0,5)}),
        ([' ', ' ', '#', '#', '#', "#", '#'], {(0,2), (0,3), (0,4), (0,5), (0,6)})
    ],
    ids=["left", "center", "right"])
def test_matches_5_horizontal(row, expected_matches):
    b = Board(rows=1, cols=7)
    # Create a vertical match of 4
    b.board = [
        row,
    ]
    matches = b.find_matches()
    # Expecting a vertical match of 4 in the first column
    assert matches == expected_matches


@pytest.mark.parametrize("single_col_board, expected_matches", 
    [
        ([['#'], ['#'], ['#'], [' '], [' ']], {(0,0), (1,0), (2,0)}),
        ([[' '], ['#'], ['#'], ['#'], [' ']], {(1,0), (2,0), (3,0)}),
        ([[' '], [' '], ['#'], ['#'], ['#']], {(2,0), (3,0), (4,0)})
    ],
    ids=["upper", "center", "lower"])
def test_matches_3_vertical(single_col_board, expected_matches):
    b = Board(rows=5, cols=1)
    b.board = single_col_board
    matches = b.find_matches()
    assert matches == expected_matches


@pytest.mark.parametrize("single_col_board, expected_matches", 
    [
        ([['#'], ['#'], ['#'], ['#'], [' '], [' ']], {(0,0), (1,0), (2,0), (3,0)}),
        ([[' '], ['#'], ['#'], ['#'], ['#'], [' ']], {(1,0), (2,0), (3,0), (4,0)}),
        ([[' '], [' '], ['#'], ['#'], ['#'], ['#']], {(2,0), (3,0), (4,0), (5,0)})
    ],
    ids=["upper", "center", "lower"])
def test_matches_4_vertical(single_col_board, expected_matches):
    b = Board(rows=6, cols=1)
    b.board = single_col_board
    matches = b.find_matches()
    assert matches == expected_matches


@pytest.mark.parametrize("single_col_board, expected_matches", 
    [
        ([['#'], ['#'], ['#'], ['#'], ['#'], [' '], [' ']], {(0,0), (1,0), (2,0), (3,0), (4,0)}),
        ([[' '], ['#'], ['#'], ['#'], ['#'], ['#'], [' ']], {(1,0), (2,0), (3,0), (4,0), (5,0)}),
        ([[' '], [' '], ['#'], ['#'], ['#'], ['#'], ['#']], {(2,0), (3,0), (4,0), (5,0), (6,0)})
    ],
    ids=["upper", "center", "lower"])
def test_matches_5_vertical(single_col_board, expected_matches):
    b = Board(rows=7, cols=1)
    b.board = single_col_board
    matches = b.find_matches()
    assert matches == expected_matches
