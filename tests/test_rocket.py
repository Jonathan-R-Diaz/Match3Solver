import pytest
from candy_crush.board import Board


@pytest.mark.parametrize("start_board, expected_board, move", 
    [
        ([
            ['r', ' ', 'r', 'r', ' '], 
            [' ', 'r', ' ', ' ', ' ']
        ], 
        [
            [' ', 'H', ' ', ' ', ' '], 
            [' ', ' ', ' ', ' ', ' ']
        ],
            (1, 1, 0, 1)
        ),
        ###
        ([
            [' ', 'r', ' ', 'r', 'r', ' '], 
            [' ', ' ', 'r', ' ', ' ', ' ']
        ], 
        [
            [' ', ' ', 'H', ' ', ' ', ' '], 
            [' ', ' ', ' ', ' ', ' ', ' ']
        ],
            (1, 2, 0, 2)
        ),
        ###
        ([
            [' ', 'r', ' ', 'r', 'r'], 
            [' ', ' ', 'r', ' ', ' ']
        ], 
        [
            [' ', ' ', 'H', ' ', ' '], 
            [' ', ' ', ' ', ' ', ' ']
        ],
            (1, 2, 0, 2)
        ),
        ###
        ([
            ['r', 'r', ' ', 'r', ' '], 
            [' ', ' ', 'r', ' ', ' ']
        ], 
        [
            [' ', ' ', 'H', ' ', ' '], 
            [' ', ' ', ' ', ' ', ' ']
        ],
            (1, 2, 0, 2)
        ),
        ###
        ([
            [' ', 'r', 'r', ' ', 'r', ' '], 
            [' ', ' ', ' ', 'r', ' ', ' ']
        ], 
        [
            [' ', ' ', ' ', 'H', ' ', ' '], 
            [' ', ' ', ' ', ' ', ' ', ' ']
        ],
            (1, 3, 0, 3)
        ),
        ###
        ([
            [' ', 'r', 'r', ' ', 'r'], 
            [' ', ' ', ' ', 'r', ' ']
        ], 
        [
            [' ', ' ', ' ', 'H', ' '], 
            [' ', ' ', ' ', ' ', ' ']
        ],
            (1, 3, 0, 3)
        ),
        ###
        ([
            [' ', 'r', ' ', ' ', ' '],
            ['r', ' ', 'r', 'r', ' ']
        ],
        [
            [' ', ' ', ' ', ' ', ' '],
            [' ', 'H', ' ', ' ', ' ']
        ],
            (0, 1, 1, 1)
        ),
        ###
        ([
            [' ', ' ', 'r', ' ', ' ', ' '],
            [' ', 'r', ' ', 'r', 'r', ' ']
        ],
        [
            [' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', 'H', ' ', ' ', ' ']
        ],
            (0, 2, 1, 2)
        ),
        ###
        ([
            [' ', ' ', 'r', ' ', ' '],
            [' ', 'r', ' ', 'r', 'r']
        ],
        [
            [' ', ' ', ' ', ' ', ' '],
            [' ', ' ', 'H', ' ', ' ']
        ],
            (0, 2, 1, 2)
        ),
        ###
        ([
            [' ', ' ', 'r', ' ', ' '],
            ['r', 'r', ' ', 'r', ' ']
        ],
        [
            [' ', ' ', ' ', ' ', ' '],
            [' ', ' ', 'H', ' ', ' ']
        ],
            (0, 2, 1, 2)
        ),
        ###
        ([
            [' ', ' ', ' ', 'r', ' ', ' '],
            [' ', 'r', 'r', ' ', 'r', ' ']
        ],
        [
            [' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', 'H', ' ', ' ']
        ],
            (0, 3, 1, 3)
        ),
        ###
        ([
            [' ', ' ', ' ', 'r', ' '],
            [' ', 'r', 'r', ' ', 'r']
        ],
        [
            [' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', 'H', ' ']
        ],
            (0, 3, 1, 3)
        ),
    ],
    # [L,R]Candy - [L,R]Aligned - Top or Bottom
    ids=["LC-LA-T", "LC-CA-T", "LC-RA-T", 
         "RC-LA-T", "RC-CA-T", "RC-RA-T",
         "LC-LA-B", "LC-CA-B", "LC-RA-B", 
         "RC-LA-B", "RC-CA-B", "RC-RA-B"
    ]
)
@pytest.mark.board
def test_spawn_rocket_horizontal(start_board, expected_board, move):
    b = Board(board_state=start_board, debug=True)
    
    r1, c1, r2, c2 = move
    b.swap(r1, c1, r2, c2)
    b.last_move = ((r1, c1), (r2, c2))

    assert b.pop() == 4
    assert b.grid == expected_board


@pytest.mark.parametrize("start_board, expected_board, move", 
    [
        ([
            ['r', ' '], 
            [' ', 'r'],
            ['r', ' '], 
            ['r', ' '], 
            [' ', ' ']
        ], 
        [
            [' ', ' '], 
            ['H', ' '],
            [' ', ' '], 
            [' ', ' '], 
            [' ', ' ']
        ],
            (1, 1, 1, 0)
        ),
        ###
        ([
            [' ', ' '],
            ['r', ' '], 
            [' ', 'r'],
            ['r', ' '], 
            ['r', ' '], 
            [' ', ' ']
        ], 
        [
            [' ', ' '],
            [' ', ' '], 
            ['H', ' '],
            [' ', ' '], 
            [' ', ' '], 
            [' ', ' ']
        ],
            (2, 1, 2, 0)
        ),
        ###
        ([
            [' ', ' '],
            ['r', ' '], 
            [' ', 'r'],
            ['r', ' '], 
            ['r', ' '], 
        ], 
        [
            [' ', ' '],
            [' ', ' '], 
            ['H', ' '],
            [' ', ' '], 
            [' ', ' '], 
        ],
            (2, 1, 2, 0)
        ),
        ###
        ([
            ['r', ' '], 
            ['r', ' '],
            [' ', 'r'], 
            ['r', ' '], 
            [' ', ' ']
        ], 
        [
            [' ', ' '], 
            [' ', ' '],
            ['H', ' '], 
            [' ', ' '], 
            [' ', ' ']
        ],
            (2, 1, 2, 0)
        ),
        ###
        ([
            [' ', ' '],
            ['r', ' '], 
            ['r', ' '],
            [' ', 'r'], 
            ['r', ' '], 
            [' ', ' ']
        ], 
        [
            [' ', ' '],
            [' ', ' '], 
            [' ', ' '],
            ['H', ' '], 
            [' ', ' '], 
            [' ', ' ']
        ],
            (3, 1, 3, 0)
        ),
        ###
        ([
            [' ', ' '],
            ['r', ' '], 
            ['r', ' '],
            [' ', 'r'], 
            ['r', ' '], 
        ], 
        [
            [' ', ' '],
            [' ', ' '], 
            [' ', ' '],
            ['H', ' '], 
            [' ', ' '], 
        ],
            (3, 1, 3, 0)
        ),
        ###
        ([
            [' ', 'r'],
            ['r', ' '],
            [' ', 'r'],
            [' ', 'r'],
            [' ', ' ']
        ],
        [
            [' ', ' '],
            [' ', 'H'],
            [' ', ' '],
            [' ', ' '],
            [' ', ' ']
        ],
            (1, 0, 1, 1)
        ),
        ###
        ([
            [' ', ' '],
            [' ', 'r'],
            ['r', ' '],
            [' ', 'r'],
            [' ', 'r'],
            [' ', ' ']
        ],
        [
            [' ', ' '],
            [' ', ' '],
            [' ', 'H'],
            [' ', ' '],
            [' ', ' '],
            [' ', ' ']
        ],
            (2, 0, 2, 1)
        ),
        ###
        ([
            [' ', ' '],
            [' ', 'r'],
            ['r', ' '],
            [' ', 'r'],
            [' ', 'r']
        ],
        [
            [' ', ' '],
            [' ', ' '],
            [' ', 'H'],
            [' ', ' '],
            [' ', ' ']
        ],
            (2, 0, 2, 1)
        ),
        ###
        ([
            [' ', 'r'],
            [' ', 'r'],
            ['r', ' '],
            [' ', 'r'],
            [' ', ' ']
        ],
        [
            [' ', ' '],
            [' ', ' '],
            [' ', 'H'],
            [' ', ' '],
            [' ', ' ']
        ],
            (2, 0, 2, 1)
        ),
        ###
        ([
            [' ', ' '],
            [' ', 'r'],
            [' ', 'r'],
            ['r', ' '],
            [' ', 'r'],
            [' ', ' ']
        ],
        [
            [' ', ' '],
            [' ', ' '],
            [' ', ' '],
            [' ', 'H'],
            [' ', ' '],
            [' ', ' ']
        ],
            (3, 0, 3, 1)
        ),
        ###
        ([
            [' ', ' '],
            [' ', 'r'],
            [' ', 'r'],
            ['r', ' '],
            [' ', 'r']
        ],
        [
            [' ', ' '],
            [' ', ' '],
            [' ', ' '],
            [' ', 'H'],
            [' ', ' ']
        ],
            (3, 0, 3, 1)
        ),
    ],
    # [T,B]Candy - [T,C,B]Aligned - Left or Right line
    ids=["TC-TA-L", "TC-CA-L", "TC-BA-L",
         "BC-TA-L", "BC-CA-L", "BC-BA-L",
         "TC-TA-R", "TC-CA-R", "TC-BA-R",
         "BC-TA-R", "BC-CA-R", "BC-BA-R"
    ]
)
@pytest.mark.board
def test_spawn_rocket_vertical(start_board, expected_board, move):
    b = Board(board_state=start_board, debug=True)
    
    r1, c1, r2, c2 = move
    b.swap(r1, c1, r2, c2)
    b.last_move = ((r1, c1), (r2, c2))

    assert b.pop() == 4
    assert b.grid == expected_board


@pytest.mark.parametrize("move, ch", 
    [
        ((1, 2, "w"), "y"),
        ((1, 2, "s"), "g"),
        ((1, 2, "x"), "r"),
        ((1, 2, "a"), "r"),
        ((1, 2, "d"), "r")

    ],
    ids = ["w", "s", "x", "a", "d"]
)
@pytest.mark.board
def test_rocket_power_horizontal(move, ch):
    b = Board(board_state=[
        ['y', 'y', '#', 'y', 'y'],
        ['r', 'r', 'H', 'r', 'r'],
        ['g', 'g', '#', 'g', 'g']
    ])

    r1, c1, d = move
    r2, c2 = b.get_neighbor(*move)
    b.swap(r1, c1, r2, c2)
    assert b.activate_powerup(r1, c1, r2, c2) == 4

    for row in b.grid:
        assert ch not in row
        assert "H" not in row


@pytest.mark.parametrize("move, ch", 
    [
        ((2, 1, "w"), "r"),
        ((2, 1, "s"), "r"),
        ((2, 1, "x"), "r"),
        ((2, 1, "a"), "y"),
        ((2, 1, "d"), "g")

    ],
    ids = ["w", "s", "x", "a", "d"]
)
@pytest.mark.board
def test_rocket_power_vertical(move, ch):
    b = Board(board_state=[
        ['y', 'r', 'g'],
        ['y', 'r', 'g'],
        ['#', 'V', '#'],
        ['y', 'r', 'g'],
        ['y', 'r', 'g']
    ])

    r1, c1, d = move
    r2, c2 = b.get_neighbor(*move)
    b.swap(r1, c1, r2, c2)
    assert b.activate_powerup(r1, c1, r2, c2) == 4

    for row in b.grid:
        assert ch not in row
        assert "H" not in row


@pytest.mark.board
def test_rocket_chain():
    b = Board(board_state=[
        [' ', 'r', ' ', ' ', ' ', 'r', ' '],
        [' ', 'r', ' ', ' ', ' ', 'r', ' '],
        ['r', 'V', 'r', 'H', 'r', 'V', 'r'],
        [' ', 'r', ' ', ' ', ' ', 'r', ' '],
        [' ', 'r', ' ', ' ', ' ', 'r', ' '],
    ])

    assert b.activate_powerup(2, 3, 2, 3) == 12

    for row in b.grid:
        for ch in row:
            assert ch == " "


@pytest.mark.board
def test_rocket_chain_heavy():
    b = Board(board_state=[
        ['r', 'H', 'r', 'r', 'r', 'H', 'r'],
        ['r', 'H', 'r', 'r', 'r', 'H', 'r'],
        ['r', 'V', 'V', 'H', 'V', 'V', 'r'],
        ['r', 'H', 'r', 'r', 'r', 'H', 'r'],
        ['r', 'H', 'r', 'r', 'r', 'H', 'r'],
    ])

    assert b.activate_powerup(2, 3, 2, 3) == 22

    for row in b.grid:
        for ch in row:
            assert ch == " "


@pytest.mark.parametrize("rkt", ["V", "H"])
def test_rocket_valid_moves(rkt):
    b = Board(board_state = [
        [' ', 'y', ' '],
        ['r', rkt, 'g'],
        [' ', 'g', ' ']
    ])
    matches = b.valid_moves()
    expected_matches = [(1,1,"x"),(1,1,"s"),(1,1,"d")]
    assert matches == expected_matches