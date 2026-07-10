import pytest
from candy_crush.game import Game


def test_game_reset_and_initial_state():
    g = Game(rows=5, cols=5, max_moves=3, seed=7)
    board = g.reset()
    assert g.moves_left == 3
    assert g.score == 0
    assert board is not None


def test_game_over_when_no_valid_moves():
    # 2x2-tile stalemate (same color always 2 apart): no swap creates a match,
    # no powerups to tap. Game must be over even with moves remaining.
    g = Game(board_state=[
        ['r', 'b', 'r', 'b'],
        ['g', 'y', 'g', 'y'],
        ['r', 'b', 'r', 'b'],
        ['g', 'y', 'g', 'y'],
    ], max_moves=10)
    assert g.board.valid_moves() == []   # documents the stalemate
    assert g.moves_left > 0
    assert g.is_over()


def test_game_step_and_is_over():
    g = Game(rows=3, cols=3, max_moves=1, seed=0)
    # Force a known board with a match so that crush returns >0
    g.board.grid = [
        ['y','y','y'],
        ['#','r','g'],
        ['b','g','b']
    ]
    board, reward, done, info = g.step((0,0,'d'))
    # Since board had a match, reward should be >=3
    assert reward >= 3
    # moves_left should decrease when a reward was obtained
    assert g.moves_left == 0
    assert g.is_over() is True
    assert 'score' in info and 'moves_left' in info


@pytest.mark.gameplay
def test_swap_create_detonate():
    board = [
        ["r", "b", "b", "T", "b", "r", "r"],
        ["r", "r", "g", "b", "r", "b", "r"],
        ["y", "b", "r", "g", "b", "r", "y"],

    ]
    game = Game(board_state=board, debug=True)
    game.render()
    r, c, d = (1, 3, "w")
    game.step((r, c, d))
    game.board.print_board()
    candies = set([candy for row in game.board.grid for candy in row])
    assert "H" in candies
    assert "T" not in candies
    expected_candies = ["r", "r", "y"]
    for i in range(3):
        assert game.board.grid[i][0] == game.board.grid[i][6] == expected_candies[i]

    
@pytest.mark.parametrize("start, end", [
    # Start
    ([
        ['#', "#", "#", " ", "#", "#", '#'],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
    ],
    # End 
    [
        ['#', '#', '#', 'r', '#', '#', '#'],
        [' ', ' ', 'r', 'r', 'r', ' ', ' '],
        [' ', 'r', 'r', 'r', 'r', 'r', ' '],
        ['r', 'r', 'r', 'r', 'r', 'r', 'r']
    ]),
    
    # Start
    ([
        ['#', "#", " ", "#", "#", "#", '#'],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
    ],
    # End 
    [
        ['#', '#', 'r', '#', '#', '#', '#'],
        [' ', 'r', 'r', 'r', ' ', ' ', ' '],
        ['r', 'r', 'r', 'r', 'r', ' ', ' '],
        ['r', 'r', 'r', 'r', 'r', 'r', ' ']
    ]),
    
    # Start
    ([
        ['#', " ", "#", "#", "#", "#", '#'],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
    ],
    # End 
    [
        ['#', 'r', '#', '#', '#', '#', '#'],
        ['r', 'r', 'r', ' ', ' ', ' ', ' '],
        ['r', 'r', 'r', 'r', ' ', ' ', ' '],
        ['r', 'r', 'r', 'r', 'r', ' ', ' ']
    ]),
    
    # Start
    ([
        [' ', "#", "#", "#", "#", "#", '#'],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
    ],
    # End 
    [
        ['r', '#', '#', '#', '#', '#', '#'],
        ['r', 'r', ' ', ' ', ' ', ' ', ' '],
        ['r', 'r', 'r', ' ', ' ', ' ', ' '],
        ['r', 'r', 'r', 'r', ' ', ' ', ' ']
    ]),
    
    # Start 
    ([
        ['#', "#", "#", "#", " ", "#", '#'],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
    ],
    # End 
    [
        ['#', '#', '#', '#', 'r', '#', '#'],
        [' ', ' ', ' ', 'r', 'r', 'r', ' '],
        [' ', ' ', 'r', 'r', 'r', 'r', 'r'],
        [' ', 'r', 'r', 'r', 'r', 'r', 'r']
    ]),
    
    # Start 
    ([
        ['#', "#", "#", "#", "#", " ", '#'],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
    ],
    # End 
    [
        ['#', '#', '#', '#', '#', 'r', '#'],
        [' ', ' ', ' ', ' ', 'r', 'r', 'r'],
        [' ', ' ', ' ', 'r', 'r', 'r', 'r'],
        [' ', ' ', 'r', 'r', 'r', 'r', 'r']
    ]),
    
    # Start 
    ([
        ['#', "#", "#", "#", "#", "#", ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
    ],
    # End 
    [
        ['#', '#', '#', '#', '#', '#', 'r'],
        [' ', ' ', ' ', ' ', ' ', 'r', 'r'],
        [' ', ' ', ' ', ' ', 'r', 'r', 'r'],
        [' ', ' ', ' ', 'r', 'r', 'r', 'r']
    ]),
    ##
    # Start
    ([
        ['#', "#", " ", " ", " ", "#", '#'],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
    ],
    # End 
    [
        ['#', '#', 'r', 'r', 'r', '#', '#'],
        [' ', 'r', 'r', 'r', 'r', 'r', ' '],
        ['r', 'r', 'r', 'r', 'r', 'r', 'r'],
        ['r', 'r', 'r', 'r', 'r', 'r', 'r']
    ]),
    
    # Start
    ([
        ['#', " ", " ", " ", " ", " ", '#'],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' ', ' '],
    ],
    # End 
    [
        ['#', 'r', 'r', 'r', 'r', 'r', '#'],
        ['r', 'r', 'r', 'r', 'r', 'r', 'r'],
        ['r', 'r', 'r', 'r', 'r', 'r', 'r'],
        ['r', 'r', 'r', 'r', 'r', 'r', 'r']
    ]),
])
@pytest.mark.gameplay
def test_drop_physics(start, end):
    game = Game(board_state=start)
    game.board.fill(fill_with="r")
    assert game.board.grid == end