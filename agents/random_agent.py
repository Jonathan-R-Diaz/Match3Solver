import random
from typing import Optional, Tuple


def random_move(board, max_tries: int = 200) -> Optional[Tuple[int, int, str]]:
	"""Return a random valid move (r, c, d) for the given Board-like object.

	If no valid move is found within max_tries, returns None.
	"""
	rows = board.rows
	cols = board.cols
	dirs = ["w", "a", "s", "d"]

	for _ in range(max_tries):
		r = random.randrange(rows)
		c = random.randrange(cols)
		d = random.choice(dirs)
		if board.is_valid_move(r, c, d):
			return (r, c, d)
	return None


if __name__ == '__main__':
	print('This module provides random_move(board) to pick a random valid move.')
