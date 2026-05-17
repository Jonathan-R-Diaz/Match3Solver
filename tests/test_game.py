from candy_crush.game import Game


def test_game_reset_and_initial_state():
    g = Game(rows=5, cols=5, max_moves=3, seed=7)
    board = g.reset()
    assert g.moves_left == 3
    assert g.score == 0
    assert board is not None


def test_game_step_and_is_over():
    g = Game(rows=3, cols=3, max_moves=1, seed=0)
    # Force a known board with a match so that crush returns >0
    g.board.board = [
        ['@','@','@'],
        ['#','$','&'],
        ['%','^','*']
    ]
    board, reward, done, info = g.step((0,0,'d'))
    # Since board had a match, reward should be >=3
    assert reward >= 3
    # moves_left should decrease when a reward was obtained
    assert g.moves_left == 0
    assert g.is_over() is True
    assert 'score' in info and 'moves_left' in info
