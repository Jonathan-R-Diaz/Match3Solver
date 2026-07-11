# Translator between RL environment and the game logic in board.py and game.py.

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from candy_crush.board import CANDIES
from candy_crush.game import Game
from candy_crush.levels import get_level

# One observation plane per symbol. Order is fixed — changing it invalidates
# any trained checkpoint.
PLANES = CANDIES + ["5", "V", "H", "T", "S", "B", "#", " "]
PLANE_INDEX = {ch: i for i, ch in enumerate(PLANES)}

# Canonical move set (matches Board.is_valid_move): down, right, tap-in-place.
DIRS = ("s", "d", "x")


class CandyCrushEnv(gym.Env):
    """Gymnasium wrapper: clear every obstacle on a level to win.

    Reward is the number of obstacles removed by the move (dense), plus
    win_bonus for clearing the board. Exposes action_masks() so MaskablePPO
    never samples an illegal move.
    """

    metadata = {"render_modes": ["human"]}

    def __init__(self, level=1, max_moves=30, seed=0,
                 box_reward=1.0, win_bonus=10.0,
                 animate=False, step_mode=False):
        super().__init__()
        self.template = get_level(level)
        self.rows = len(self.template)
        self.cols = len(self.template[0])
        self.max_moves = max_moves
        self.base_seed = seed
        self.box_reward = box_reward
        self.win_bonus = win_bonus
        # terminal animation of crushes/cascades (watching only — leave off
        # for training, frame recording costs time)
        self.animate = animate
        self.step_mode = step_mode
        self._episode = 0
        self.game = None

        self.observation_space = spaces.Box(
            low=0.0, high=1.0, shape=(len(PLANES), self.rows, self.cols),
            dtype=np.float32,
        )
        self.action_space = spaces.Discrete(self.rows * self.cols * len(DIRS))

    # --- move <-> action index ------------------------------------------------

    def encode_action(self, r, c, d):
        return (r * self.cols + c) * len(DIRS) + DIRS.index(d)

    def decode_action(self, action):
        action = int(action)
        d = DIRS[action % len(DIRS)]
        cell = action // len(DIRS)
        return cell // self.cols, cell % self.cols, d

    # --- gym API ----------------------------------------------------------------

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        # Fresh deal each episode on the same layout; Game.reset() alone
        # would replay the identical deal every time.
        if seed is not None:
            self.base_seed = seed
        deal_seed = self.base_seed + self._episode
        self._episode += 1
        self.game = Game(
            board_state=self.template,
            max_moves=self.max_moves,
            seed=deal_seed,
            fill_empty=True,
            freeplay=False,
            verbose=False,
        )
        return self._obs(), self._info()

    def step(self, action):
        move = self.decode_action(action)
        before = self._obstacle_count()
        self.game.step(move, animate=self.animate, step_mode=self.step_mode)
        after = self._obstacle_count()

        won = after == 0
        stalemate = not won and len(self.game.board.valid_moves()) == 0

        reward = (before - after) * self.box_reward
        if won:
            reward += self.win_bonus

        terminated = won or stalemate
        truncated = not terminated and self.game.moves_left <= 0
        return self._obs(), reward, terminated, truncated, self._info(won=won)

    def action_masks(self):
        mask = np.zeros(self.action_space.n, dtype=bool)
        for r, c, d in self.game.board.valid_moves():
            mask[self.encode_action(r, c, d)] = True
        return mask

    def render(self):
        self.game.render()

    # --- internals ----------------------------------------------------------------

    def _obstacle_count(self):
        return sum(self.game.board.get_obstacles().values())

    def _obs(self):
        obs = np.zeros((len(PLANES), self.rows, self.cols), dtype=np.float32)
        for r in range(self.rows):
            for c in range(self.cols):
                obs[PLANE_INDEX[self.game.board.grid[r][c]], r, c] = 1.0
        return obs

    def _info(self, won=False):
        return {
            "obstacles": self._obstacle_count(),
            "score": self.game.score,
            "moves_left": self.game.moves_left,
            "is_success": won,
        }
