import numpy as np
import pytest

from rl.env import CandyCrushEnv, DIRS, PLANES, PLANE_INDEX
from candy_crush.levels import get_level


@pytest.fixture
def env():
    e = CandyCrushEnv(level=1, max_moves=30, seed=0)
    e.reset()
    return e


@pytest.mark.env
def test_action_encode_decode_roundtrip(env):
    for r in range(env.rows):
        for c in range(env.cols):
            for d in DIRS:
                a = env.encode_action(r, c, d)
                assert 0 <= a < env.action_space.n
                assert env.decode_action(a) == (r, c, d)


@pytest.mark.env
def test_action_mask_matches_valid_moves(env):
    mask = env.action_masks()
    expected = {env.encode_action(r, c, d)
                for r, c, d in env.game.board.valid_moves()}
    assert set(np.flatnonzero(mask)) == expected
    assert mask.any()  # a fresh deal always has at least one move


@pytest.mark.env
def test_obs_is_one_hot_and_matches_grid(env):
    obs, _ = env.reset()
    assert obs.shape == (len(PLANES), env.rows, env.cols)
    # exactly one plane set per cell
    assert np.array_equal(obs.sum(axis=0), np.ones((env.rows, env.cols)))
    for r in range(env.rows):
        for c in range(env.cols):
            ch = env.game.board.grid[r][c]
            assert obs[PLANE_INDEX[ch], r, c] == 1.0


@pytest.mark.env
def test_reward_is_obstacle_delta_not_candies(env):
    # Take any legal move; reward must equal boxes removed, regardless of
    # how many candies the move crushed.
    before = env._obstacle_count()
    action = int(np.flatnonzero(env.action_masks())[0])
    _, reward, _, _, info = env.step(action)
    assert reward == before - info["obstacles"]
    assert env.game.score > 0  # candies did crush — but weren't rewarded as such


@pytest.mark.env
def test_win_gives_bonus_and_terminates(env):
    # Cheat the board into a nearly-cleared state: one box left, with a
    # guaranteed match next to it.
    grid = env.game.board.grid
    for r in range(env.rows):
        for c in range(env.cols):
            grid[r][c] = ["r", "b", "g", "y"][(r + 2 * c) % 4]  # matchless tiling
    grid[8][0] = "B"
    grid[7][0] = "r"
    grid[7][1] = "r"
    grid[7][2] = "b"
    grid[6][2] = "r"
    # swapping (6,2) down makes row 7 = r,r,r — matched (7,0) is adjacent to the box
    obs, reward, terminated, truncated, info = env.step(env.encode_action(6, 2, "s"))
    assert info["obstacles"] == 0
    assert reward == 1 * env.box_reward + env.win_bonus
    assert terminated and not truncated
    assert info["is_success"]


@pytest.mark.env
def test_truncates_when_moves_run_out():
    env = CandyCrushEnv(level=1, max_moves=1, seed=0)
    env.reset()
    action = int(np.flatnonzero(env.action_masks())[0])
    _, _, terminated, truncated, _ = env.step(action)
    assert truncated and not terminated


@pytest.mark.env
def test_reset_same_seed_same_deal():
    a = CandyCrushEnv(level=1, seed=42)
    b = CandyCrushEnv(level=1, seed=42)
    obs_a, _ = a.reset()
    obs_b, _ = b.reset()
    assert np.array_equal(obs_a, obs_b)


@pytest.mark.env
def test_reset_advances_the_deal():
    env = CandyCrushEnv(level=1, seed=0)
    obs1, _ = env.reset()
    obs2, _ = env.reset()
    assert not np.array_equal(obs1, obs2)  # new episode, new deal
    # layout itself is preserved: box/wall planes identical
    for ch in ("B", "#"):
        i = PLANE_INDEX[ch]
        assert np.array_equal(obs1[i], obs2[i])


@pytest.mark.env
def test_reset_deal_is_always_playable():
    # Level-1 seed 1186 deals a board with zero legal moves (crashed a real
    # training run at ~update 70). The board auto-reshuffles, so every
    # episode the env serves must start with at least one legal action.
    env = CandyCrushEnv(level=1, max_moves=15, seed=1186)
    env.reset()
    assert env.action_masks().any()


@pytest.mark.env
def test_level_template_not_mutated_by_episodes():
    env = CandyCrushEnv(level=1, seed=0)
    env.reset()
    for _ in range(3):
        legal = np.flatnonzero(env.action_masks())
        _, _, terminated, truncated, _ = env.step(int(legal[0]))
        if terminated or truncated:
            break
    assert env.template == get_level(1)
