# Translator between RL environment and the game logic in board.py and game.py.

from candy_crush.board import Board
from candy_crush.game import Game

class CandyCrushEnv:

    def __init__(self, rows=5, cols=5, max_moves=20, seed=0):
        self.game = Game(rows=rows, cols=cols, max_moves=max_moves, seed=seed)

    def reset(self):
        return self.game.reset()

    def step(self, move):
        return self.game.step(move)

    def render(self):
        self.game.render()

    def is_over(self):
        return self.game.is_over()