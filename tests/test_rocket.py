import pytest
from candy_crush.board import Board


@pytest.mark.skip
def test_find_4_in_a_row():
    b = Board(rows=5, cols=5)
    # Create a vertical match of 4
    b.board = [
        ['#', '@', '@', '@', '@'],
        ['#', ' ', ' ', ' ', ' '],
        ['#', ' ', ' ', ' ', ' '],
        ['#', ' ', ' ', ' ', ' '],
        ['$', ' ', ' ', ' ', ' ']
    ]
    matches = b.find_matches()
    # Expecting a vertical match of 4 in the first column
    expected_matches = {(0,0), (1,0), (2,0), (3,0), (0,1), (0,2), (0,3), (0,4)}  # The 4 in a row plus the 4 in the first row
    assert matches == expected_matches


@pytest.mark.skip
def test_create_4_powerup_board():
    b = Board(rows=5, cols=6)
    # Create a horizontal match of 5 to test power-up creation
    b.board = [
        ['@', '$', ' ', '$', '$', ' '],
        ['@', ' ', '$', ' ', ' ', ' '],
        ['@', ' ', '#', '#', ' ', '#'],
        ['@', ' ', ' ', ' ', '#', ' '],
        ['@', ' ', ' ', ' ', ' ', ' ']
    ]

    b.crush(refill=False)  # This should create a power-up in the middle of the first column
    
    expected_board = [
        [' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' '],
        ['4', ' ', '4', ' ', '4', ' ']
    ]
    assert b.board == expected_board  # Check that the power-up was created in the expected location

