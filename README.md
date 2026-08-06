# candy-crush-ml

A match-3 engine built from scratch, an RL agent trained to play it, and a
vision pipeline that lets the trained agent play the real mobile game.

The target game is **Royal Kingdom** (Dream Games), played on an Android
phone. The engine mirrors its rules directly — same candies, same powerups,
same box-clearing objective — so a policy trained against the engine
transfers to real screenshots of the real app.

## What's here

**`candy_crush/`** — the game engine. A pure-Python board (`board.py`) with
match detection, cascades, five powerups (light ball, vertical/horizontal
rocket, TNT, propeller) and their pairwise combos, plus box obstacles that
must be cleared to win. `game.py` wraps it into a playable session with a
move budget; `levels.py` holds hand-built layouts. No external game
dependencies — this is a from-scratch reimplementation.

**`rl/`** — a [Gymnasium](https://gymnasium.farama.org/) environment
(`env.py`) around the engine: one-hot board observations, an action mask so
the policy only ever sees legal moves, and a reward built around the actual
objective (obstacles cleared, not candies popped). `policy.py` is a small
CNN policy/value network.

**`train.py`** — hand-rolled REINFORCE-with-baseline in PyTorch (no
stable-baselines3 or other RL library). Trains until you stop it, auto-
resumes from checkpoints, and logs a random-policy baseline so progress is
always measured against something.

**`vision/`** — the real-world bridge. Takes a screenshot of the actual
Android game, auto-detects the board's grid from its border, classifies
each cell (hue matching for candies, template matching for powerup
sprites), and feeds the parsed board to a trained checkpoint for a move
suggestion. `vision/play_live.py` drives the loop end to end: screenshot →
suggest → you play it on the phone → repeat.

**`tests/`** — pytest suite covering the engine, the RL environment, and
the vision pipeline (200+ tests).

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# play the engine yourself in the terminal
python play.py

# train an agent (Ctrl-C to stop; it checkpoints as it goes)
python train.py --moves 15

# watch a trained checkpoint play
python scripts/watch.py models/reinforce_level1.pt

# suggest moves for a real game running on a connected Android phone
python vision/play_live.py
```

## Status

Actively evolving — level layouts, obstacle types, and reward shaping are
all in flux as the agent's training catches up to the vision pipeline's
ability to read new levels off the real game.
