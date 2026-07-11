"""Policy network for the hand-rolled REINFORCE agent."""
import math

import torch
import torch.nn as nn
from torch.distributions import Categorical


class PolicyNet(nn.Module):
    """Shared-trunk MLP: one-hot board in, masked action logits + state value out.

    The value head is the REINFORCE baseline: it predicts the return from a
    state so the policy gradient only sees how much better/worse an action
    did than expected, which cuts variance enormously.
    """

    def __init__(self, obs_shape, n_actions, hidden=256):
        super().__init__()
        self.obs_shape = tuple(obs_shape)
        self.n_actions = n_actions
        obs_size = math.prod(obs_shape)
        self.trunk = nn.Sequential(
            nn.Flatten(),
            nn.Linear(obs_size, hidden), nn.ReLU(),
            nn.Linear(hidden, hidden), nn.ReLU(),
        )
        self.policy_head = nn.Linear(hidden, n_actions)
        self.value_head = nn.Linear(hidden, 1)

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


def save_checkpoint(net, path, **meta):
    torch.save({
        "state_dict": net.state_dict(),
        "obs_shape": net.obs_shape,
        "n_actions": net.n_actions,
        **meta,
    }, path)


def load_checkpoint(path):
    ckpt = torch.load(path, weights_only=False)
    net = PolicyNet(ckpt["obs_shape"], ckpt["n_actions"])
    net.load_state_dict(ckpt["state_dict"])
    net.eval()
    return net, ckpt
