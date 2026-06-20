import pytest
from candy_crush.board import Board


@pytest.mark.parametrize("start_board, expected_board, move", 
    [
        ([
            ['$', ' ', '$', '$', ' '], 
            [' ', '$', ' ', ' ', ' ']
        ], 
        [
            [' ', '4', ' ', ' ', ' '], 
            [' ', ' ', ' ', ' ', ' ']
        ],
            (1, 1, 0, 1)
        ),
        ###
        ([
            [' ', '$', ' ', '$', '$', ' '], 
            [' ', ' ', '$', ' ', ' ', ' ']
        ], 
        [
            [' ', ' ', '4', ' ', ' ', ' '], 
            [' ', ' ', ' ', ' ', ' ', ' ']
        ],
            (1, 2, 0, 2)
        ),
        ###
        ([
            [' ', '$', ' ', '$', '$'], 
            [' ', ' ', '$', ' ', ' ']
        ], 
        [
            [' ', ' ', '4', ' ', ' '], 
            [' ', ' ', ' ', ' ', ' ']
        ],
            (1, 2, 0, 2)
        ),
        ###
        ([
            ['$', '$', ' ', '$', ' '], 
            [' ', ' ', '$', ' ', ' ']
        ], 
        [
            [' ', ' ', '4', ' ', ' '], 
            [' ', ' ', ' ', ' ', ' ']
        ],
            (1, 2, 0, 2)
        ),
        ###
        ([
            [' ', '$', '$', ' ', '$', ' '], 
            [' ', ' ', ' ', '$', ' ', ' ']
        ], 
        [
            [' ', ' ', ' ', '4', ' ', ' '], 
            [' ', ' ', ' ', ' ', ' ', ' ']
        ],
            (1, 3, 0, 3)
        ),
        ###
        ([
            [' ', '$', '$', ' ', '$'], 
            [' ', ' ', ' ', '$', ' ']
        ], 
        [
            [' ', ' ', ' ', '4', ' '], 
            [' ', ' ', ' ', ' ', ' ']
        ],
            (1, 3, 0, 3)
        ),
        ###
    ],
    ids=["left candy-left edge", "left candy-center", "left candy-right edge", "right candy-left edge", "right candy-center", "right candy-right edge"]
)
def test_spawn_rocket_horizontal(start_board, expected_board, move):
    b = Board(board_state=start_board)
    
    print(move)
    r1, c1, r2, c2 = move
    b.swap(r1, c1, r2, c2)
    b.last_move = ((r1, c1), (r2, c2))

    assert b.pop() == 4
    assert b.board == expected_board


@pytest.mark.parametrize("start_board, expected_board, move", 
    [
        ([
            ['$', ' '], 
            [' ', '$'],
            ['$', ' '], 
            ['$', ' '], 
            [' ', ' ']
        ], 
        [
            [' ', ' '], 
            ['4', ' '],
            [' ', ' '], 
            [' ', ' '], 
            [' ', ' ']
        ],
            (1, 1, 1, 0)
        ),
        ###
        ([
            [' ', ' '],
            ['$', ' '], 
            [' ', '$'],
            ['$', ' '], 
            ['$', ' '], 
            [' ', ' ']
        ], 
        [
            [' ', ' '],
            [' ', ' '], 
            ['4', ' '],
            [' ', ' '], 
            [' ', ' '], 
            [' ', ' ']
        ],
            (2, 1, 2, 0)
        ),
        ###
        ([
            [' ', ' '],
            ['$', ' '], 
            [' ', '$'],
            ['$', ' '], 
            ['$', ' '], 
        ], 
        [
            [' ', ' '],
            [' ', ' '], 
            ['4', ' '],
            [' ', ' '], 
            [' ', ' '], 
        ],
            (2, 1, 2, 0)
        ),
        ###
        ([
            ['$', ' '], 
            ['$', ' '],
            [' ', '$'], 
            ['$', ' '], 
            [' ', ' ']
        ], 
        [
            [' ', ' '], 
            [' ', ' '],
            ['4', ' '], 
            [' ', ' '], 
            [' ', ' ']
        ],
            (2, 1, 2, 0)
        ),
        ###
        ([
            [' ', ' '],
            ['$', ' '], 
            ['$', ' '],
            [' ', '$'], 
            ['$', ' '], 
            [' ', ' ']
        ], 
        [
            [' ', ' '],
            [' ', ' '], 
            [' ', ' '],
            ['4', ' '], 
            [' ', ' '], 
            [' ', ' ']
        ],
            (3, 1, 3, 0)
        ),
        ###
        ([
            [' ', ' '],
            ['$', ' '], 
            ['$', ' '],
            [' ', '$'], 
            ['$', ' '], 
        ], 
        [
            [' ', ' '],
            [' ', ' '], 
            [' ', ' '],
            ['4', ' '], 
            [' ', ' '], 
        ],
            (3, 1, 3, 0)
        )
    ],
    ids=["upper_candy-upper_edge", "upper_candy-center", "upper_candy-lower_edge",
         "lower_candy-upper_edge", "lower_candy-center", "lower_candy-lower_edge"]
)
def test_spawn_rocket_vertical(start_board, expected_board, move):
    b = Board(board_state=start_board)
    
    print(move)
    r1, c1, r2, c2 = move
    b.swap(r1, c1, r2, c2)
    b.last_move = ((r1, c1), (r2, c2))

    assert b.pop() == 4
    assert b.board == expected_board