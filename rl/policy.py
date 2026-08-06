"""Policy network for the hand-rolled REINFORCE agent."""
import math

import torch
import torch.nn as nn
from torch.distributions import Categorical


class _SharedTrunkNet(nn.Module):
    """Shared trunk, two heads: masked action logits + state value.

    The value head is the REINFORCE baseline: it predicts the return from a
    state so the policy gradient only sees how much better/worse an action
    did than expected, which cuts variance enormously.
    """

    def forward(self, obs, mask):
        """obs (B, planes, R, C) float32; mask (B, n_actions) bool.
        Returns (logits with illegal actions at -1e9, value estimates)."""
        h = self.trunk(obs)
        # -1e9 instead of -inf: softmax still gives ~0 probability, but
        # entropy/log_prob stay NaN-free.
        logits = self.policy_head(h).masked_fill(~mask, -1e9)
        return logits, self.value_head(h).squeeze(-1)

    @torch.no_grad()
    def act(self, obs, mask, greedy=False):
        """Pick one action for a single (unbatched) observation."""
        logits, _ = self(obs.unsqueeze(0), mask.unsqueeze(0))
        if greedy:
            return int(logits.argmax())
        return int(Categorical(logits=logits).sample())


class PolicyNet(_SharedTrunkNet):
    """CNN trunk: conv layers see the board as a 2-D grid, so "candy pair next
    to a box" is one filter applied everywhere instead of 81 per-cell weights.
    """

    arch = "cnn"

    def __init__(self, obs_shape, n_actions, channels=64, hidden=256):
        super().__init__()
        self.obs_shape = tuple(obs_shape)
        self.n_actions = n_actions
        planes, rows, cols = self.obs_shape
        self.trunk = nn.Sequential(
            nn.Conv2d(planes, channels, 3, padding=1), nn.ReLU(),
            nn.Conv2d(channels, channels, 3, padding=1), nn.ReLU(),
            nn.Conv2d(channels, channels, 3, padding=1), nn.ReLU(),
            nn.Flatten(),
            nn.Linear(channels * rows * cols, hidden), nn.ReLU(),
        )
        self.policy_head = nn.Linear(hidden, n_actions)
        self.value_head = nn.Linear(hidden, 1)


class MlpPolicyNet(_SharedTrunkNet):
    """The original flatten-everything MLP trunk. Kept so checkpoints saved
    before the CNN switch still load (they have no "arch" field)."""

    arch = "mlp"

    def __init__(self, obs_shape, n_actions, hidden=256):
        super().__init__()
        self.obs_shape = tuple(obs_shape)
        self.n_actions = n_actions
        self.trunk = nn.Sequential(
            nn.Flatten(),
            nn.Linear(math.prod(obs_shape), hidden), nn.ReLU(),
            nn.Linear(hidden, hidden), nn.ReLU(),
        )
        self.policy_head = nn.Linear(hidden, n_actions)
        self.value_head = nn.Linear(hidden, 1)


ARCHS = {cls.arch: cls for cls in (PolicyNet, MlpPolicyNet)}


def save_checkpoint(net, path, **meta):
    torch.save({
        "state_dict": net.state_dict(),
        "obs_shape": net.obs_shape,
        "n_actions": net.n_actions,
        "arch": net.arch,
        **meta,
    }, path)


def load_checkpoint(path):
    ckpt = torch.load(path, weights_only=False)
    cls = ARCHS[ckpt.get("arch", "mlp")]
    net = cls(ckpt["obs_shape"], ckpt["n_actions"])
    net.load_state_dict(ckpt["state_dict"])
    net.eval()
    return net, ckpt
