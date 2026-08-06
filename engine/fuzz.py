"""Random-play fuzzing: exercise the engine with invariants on.

Each game runs with debug=True, so Board.validate() is enforced after every
step; any violation or crash produces a paste-able repro block
(seed + initial board + move history) for scripts/replay.py.
"""
import contextlib
import io
import random

from candy_crush.game import Game


def fuzz_game(seed: int, max_moves: int = 40, rows: int = 8, cols: int = 8):
    """Play one random game to completion. Returns None, or a repro string on failure."""
    rng = random.Random(seed ^ 0xF00D)
    game = None
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            game = Game(rows=rows, cols=cols, max_moves=max_moves, seed=seed, debug=True, freeplay=True)
            while not game.is_over():
                moves = game.board.valid_moves()
                if not moves:
                    break
                game.step(rng.choice(moves))
        return None
    except Exception as e:
        lines = [f"seed={seed} rows={rows} cols={cols} max_moves={max_moves}"]
        if game is not None:
            lines.append(f"initial_board={game.initial_board!r}")
            lines.append(f"move_history={game.move_history!r}")
        lines.append(f"{type(e).__name__}: {e}")
        return "\n".join(lines)
