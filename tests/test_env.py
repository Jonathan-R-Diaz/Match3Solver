import numpy as np
import pytest

from rl.env import CandyCrushEnv, DIRS, PLANES, PLANE_INDEX
from engine.levels import get_level


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
def test_reward_is_obstacle_delta_not_candies():
    # Take any legal move; reward must equal boxes removed, regardless of
    # how many candies the move crushed. Shaping off — this pins the base
    # objective.
    env = CandyCrushEnv(level=1, max_moves=30, seed=0, powerup_coef=0.0)
    env.reset()
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
@pytest.mark.skip
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
def test_cnn_checkpoint_roundtrip(tmp_path, env):
    import torch
    from rl.policy import PolicyNet, save_checkpoint, load_checkpoint

    net = PolicyNet(env.observation_space.shape, env.action_space.n)
    path = str(tmp_path / "ckpt.pt")
    save_checkpoint(net, path, level=1, update=7)
    loaded, ckpt = load_checkpoint(path)
    assert isinstance(loaded, PolicyNet)
    assert ckpt["arch"] == "cnn"
    assert ckpt["update"] == 7
    obs, _ = env.reset()
    mask = torch.from_numpy(env.action_masks())
    action = loaded.act(torch.from_numpy(obs), mask, greedy=True)
    assert mask[action]  # masking holds: greedy pick is a legal move


@pytest.mark.env
def test_pre_cnn_checkpoint_loads_as_mlp(tmp_path, env):
    # checkpoints saved before the CNN switch have no "arch" field — they
    # must come back as the legacy MLP, not crash into the conv net
    import torch
    from rl.policy import MlpPolicyNet, load_checkpoint

    net = MlpPolicyNet(env.observation_space.shape, env.action_space.n)
    path = str(tmp_path / "old.pt")
    torch.save({"state_dict": net.state_dict(),
                "obs_shape": net.obs_shape,
                "n_actions": net.n_actions}, path)
    loaded, _ = load_checkpoint(path)
    assert isinstance(loaded, MlpPolicyNet)


def _rig_rocket_swap(env):
    """Overwrite the deal with a matchless tiling, one far-away box, and a
    swap at (6,2,'s') that completes a horizontal 4-run → rocket at (7,2)."""
    grid = env.game.board.grid
    for r in range(env.rows):
        for c in range(env.cols):
            grid[r][c] = ["r", "b", "g", "y"][(r + 2 * c) % 4]
    grid[0][8] = "B"  # keeps the episode from being an instant win
    grid[7][0] = "r"
    grid[7][1] = "r"
    grid[7][2] = "b"
    grid[7][3] = "r"
    grid[6][2] = "r"
    grid[6][1] = "y"  # tiling puts an r here, which would pre-match row 6
    return env.encode_action(6, 2, "s")


@pytest.mark.env
def test_powerup_creation_pays_shaping_bonus():
    env = CandyCrushEnv(level=1, max_moves=30, seed=0,
                        powerup_coef=0.5, gamma=0.99)
    env.reset()
    action = _rig_rocket_swap(env)
    _, reward, terminated, truncated, info = env.step(action)
    assert not terminated and not truncated
    phi_after = env._powerup_potential()
    assert phi_after >= 1.0  # the 4-run left a rocket behind
    base = (1 - info["obstacles"]) * env.box_reward
    assert reward == pytest.approx(base + env.powerup_coef * env.gamma * phi_after)


@pytest.mark.env
def test_powerup_hoarded_at_truncation_earns_nothing():
    # Same rigged move, but it's the episode's last: terminal potential is
    # zero, so a powerup carried into the horizon adds no reward.
    env = CandyCrushEnv(level=1, max_moves=1, seed=0,
                        powerup_coef=0.5, gamma=0.99)
    env.reset()
    action = _rig_rocket_swap(env)
    _, reward, terminated, truncated, info = env.step(action)
    assert truncated and not terminated
    assert env._powerup_potential() >= 1.0  # rocket is on the board...
    assert reward == pytest.approx((1 - info["obstacles"]) * env.box_reward)


@pytest.mark.env
def test_powerup_shaping_on_by_default():
    assert CandyCrushEnv(level=1).powerup_coef > 0


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
