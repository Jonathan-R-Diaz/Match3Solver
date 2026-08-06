"""Hand-rolled REINFORCE-with-baseline in PyTorch. Run from the repo root:

    python train.py --level 1 --updates 300

Per update: collect a batch of full episodes with the current policy, compute
returns-to-go, and take one gradient step on
    policy loss  = -log pi(a|s) * advantage      (advantage = return - value)
    value loss   = (return - value)^2            (the baseline learning)
    entropy bonus                                (keeps exploration alive)

Logs a random-masked-policy baseline first — training only counts if the
learned policy beats it. Checkpoints land in models/reinforce_level<N>.pt and
every run auto-resumes from there, so repeated runs keep learning; pass
--fresh to start a new net (watch a checkpoint with scripts/watch.py).
"""
import os
from argparse import ArgumentParser

import numpy as np
import torch
from torch.distributions import Categorical

from rl.env import CandyCrushEnv
from rl.policy import PolicyNet, save_checkpoint


def evaluate(env, choose, episodes):
    """Play episodes with choose(obs, mask) -> action. Returns (mean obstacles
    cleared, win rate, mean episode reward)."""
    cleared, wins, rewards = [], 0, []
    for _ in range(episodes):
        obs, info = env.reset()
        start = info["obstacles"]
        total = 0.0
        while True:
            action = choose(obs, env.action_masks())
            obs, reward, terminated, truncated, info = env.step(action)
            total += reward
            if terminated or truncated:
                break
        cleared.append(start - info["obstacles"])
        wins += info["is_success"]
        rewards.append(total)
    return float(np.mean(cleared)), wins / episodes, float(np.mean(rewards))


def run_episode(env, net):
    """One episode with the current (stochastic) policy.
    Returns per-step tensors plus (obstacles cleared, won)."""
    obs_l, mask_l, act_l, rew_l = [], [], [], []
    obs, info = env.reset()
    start = info["obstacles"]
    while True:
        obs_t = torch.from_numpy(obs)
        mask_t = torch.from_numpy(env.action_masks())
        action = net.act(obs_t, mask_t)
        obs, reward, terminated, truncated, info = env.step(action)
        obs_l.append(obs_t)
        mask_l.append(mask_t)
        act_l.append(action)
        rew_l.append(reward)
        if terminated or truncated:
            break
    return obs_l, mask_l, act_l, rew_l, start - info["obstacles"], info["is_success"]


def returns_to_go(rewards, gamma):
    """Discounted sum of future rewards at every step of one episode."""
    out, g = [], 0.0
    for r in reversed(rewards):
        g = r + gamma * g
        out.append(g)
    return out[::-1]


def main():
    parser = ArgumentParser()
    parser.add_argument('--level', type=int, default=1)
    parser.add_argument('--updates', type=int, default=0,
                        help='gradient steps to run; 0 = forever (Ctrl-C to '
                             'stop — progress is checkpointed either way)')
    parser.add_argument('--batch-episodes', type=int, default=16,
                        help='episodes collected per gradient step')
    parser.add_argument('--moves', type=int, default=30, help='max moves per episode')
    parser.add_argument('--lr', type=float, default=3e-4)
    parser.add_argument('--gamma', type=float, default=0.99)
    parser.add_argument('--entropy-coef', type=float, default=0.01)
    parser.add_argument('--powerup-coef', type=float, default=0.5,
                        help='weight on the powerup-creation shaping term '
                             '(potential-based, 0 disables)')
    parser.add_argument('--value-coef', type=float, default=0.5)
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--eval-episodes', type=int, default=50)
    parser.add_argument('--log-every', type=int, default=10)
    parser.add_argument('--out', default='models')
    parser.add_argument('--fresh', action='store_true',
                        help="start a new net instead of auto-resuming this "
                             "level's existing checkpoint")
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    env = CandyCrushEnv(level=args.level, max_moves=args.moves, seed=args.seed,
                        powerup_coef=args.powerup_coef, gamma=args.gamma)
    # eval reward stays unshaped so runs with different coefs are comparable
    eval_env = CandyCrushEnv(level=args.level, max_moves=args.moves,
                             seed=1_000_000, powerup_coef=0.0)

    rng = np.random.default_rng(args.seed)

    def random_policy(obs, mask):
        return int(rng.choice(np.flatnonzero(mask)))

    base = evaluate(eval_env, random_policy, args.eval_episodes)
    print(f"random baseline: {base[0]:.1f} obstacles/ep, "
          f"win rate {base[1]:.0%}, reward {base[2]:.1f}")

    net = PolicyNet(env.observation_space.shape, env.action_space.n)
    opt = torch.optim.Adam(net.parameters(), lr=args.lr)

    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, f"reinforce_level{args.level}.pt")

    start_update = 0
    if not args.fresh and os.path.exists(path):
        ckpt = torch.load(path, weights_only=False)
        if ckpt.get("arch", "mlp") != net.arch:
            backup = f"{path}.{ckpt.get('arch', 'mlp')}-bak"
            os.replace(path, backup)
            print(f"checkpoint {path} is a different architecture "
                  f"({ckpt.get('arch', 'mlp')} vs {net.arch}) — moved it to "
                  f"{backup} (still watchable) and starting fresh")
        else:
            net.load_state_dict(ckpt["state_dict"])
            if "opt_state" in ckpt:
                opt.load_state_dict(ckpt["opt_state"])
            start_update = ckpt.get("update", 0)
            # fresh deals and a fresh sampling stream — otherwise the resumed
            # run replays exactly the episodes the checkpoint already saw
            env._episode = start_update * args.batch_episodes
            torch.manual_seed(args.seed + start_update)
            print(f"resumed {path} at update {start_update}")

    update = start_update
    try:
      while args.updates <= 0 or update < start_update + args.updates:
        update += 1
        batch_obs, batch_mask, batch_act, batch_ret = [], [], [], []
        cleared_stats, win_stats = [], []
        for _ in range(args.batch_episodes):
            obs_l, mask_l, act_l, rew_l, cleared, won = run_episode(env, net)
            batch_obs += obs_l
            batch_mask += mask_l
            batch_act += act_l
            batch_ret += returns_to_go(rew_l, args.gamma)
            cleared_stats.append(cleared)
            win_stats.append(won)

        obs_t = torch.stack(batch_obs)
        mask_t = torch.stack(batch_mask)
        act_t = torch.tensor(batch_act)
        ret_t = torch.tensor(batch_ret, dtype=torch.float32)

        # one forward pass over the whole batch, this time with gradients
        logits, values = net(obs_t, mask_t)
        dist = Categorical(logits=logits)

        adv = ret_t - values.detach()
        adv = (adv - adv.mean()) / (adv.std() + 1e-8)

        policy_loss = -(dist.log_prob(act_t) * adv).mean()
        value_loss = (ret_t - values).pow(2).mean()
        entropy = dist.entropy().mean()
        loss = policy_loss + args.value_coef * value_loss - args.entropy_coef * entropy

        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(net.parameters(), 0.5)
        opt.step()

        if update % args.log_every == 0:
            print(f"update {update:4d} | "
                  f"cleared {np.mean(cleared_stats):5.1f} | "
                  f"win {np.mean(win_stats):4.0%} | "
                  f"entropy {entropy.item():.2f} | "
                  f"vloss {value_loss.item():.1f}")
            save_checkpoint(net, path, level=args.level, update=update,
                            opt_state=opt.state_dict())
    except KeyboardInterrupt:
        print(f"\nstopped at update {update}")

    save_checkpoint(net, path, level=args.level, update=update,
                    opt_state=opt.state_dict())
    print(f"saved {path}")

    def greedy_policy(obs, mask):
        return net.act(torch.from_numpy(obs), torch.from_numpy(mask), greedy=True)

    trained = evaluate(eval_env, greedy_policy, args.eval_episodes)
    print(f"random baseline: {base[0]:.1f} obstacles/ep, "
          f"win rate {base[1]:.0%}, reward {base[2]:.1f}")
    print(f"trained policy:  {trained[0]:.1f} obstacles/ep, "
          f"win rate {trained[1]:.0%}, reward {trained[2]:.1f}")


if __name__ == "__main__":
    main()
