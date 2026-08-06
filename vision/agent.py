"""A trained checkpoint, pointed at a parsed board instead of the gym env."""
import numpy as np
import torch

from candy_crush.board import Board
from rl.env import DIRS, PLANES, PLANE_INDEX
from rl.policy import load_checkpoint


class PolicyAgent:
    """Wraps a train.py checkpoint. Feed it a board grid (from BoardReader),
    get back the greedy legal move as (r, c, d) — or None on a stalemate.

    The legality mask comes from the engine's own Board.valid_moves() run on
    the parsed grid, so the net can only ever suggest moves the engine
    believes in. If the real game disagrees, the calibration (or the engine's
    mechanics) is what needs fixing — not this class.
    """

    def __init__(self, checkpoint_path):
        self.net, self.ckpt = load_checkpoint(checkpoint_path)
        self.obs_shape = tuple(self.ckpt["obs_shape"])

    def pick(self, grid, greedy=True):
        rows, cols = len(grid), len(grid[0])
        if (len(PLANES), rows, cols) != self.obs_shape:
            raise ValueError(
                f"board is {rows}x{cols} but the checkpoint was trained on "
                f"{self.obs_shape[1]}x{self.obs_shape[2]} — train a net for "
                f"this level shape first")

        board = Board(board_state=[row.copy() for row in grid])
        moves = board.valid_moves()
        if not moves:
            return None

        obs = np.zeros((len(PLANES), rows, cols), dtype=np.float32)
        for r in range(rows):
            for c in range(cols):
                obs[PLANE_INDEX[grid[r][c]], r, c] = 1.0

        mask = np.zeros(rows * cols * len(DIRS), dtype=bool)
        for r, c, d in moves:
            mask[(r * cols + c) * len(DIRS) + DIRS.index(d)] = True

        action = self.net.act(torch.from_numpy(obs), torch.from_numpy(mask),
                              greedy=greedy)
        d = DIRS[action % len(DIRS)]
        cell = action // len(DIRS)
        return cell // cols, cell % cols, d
