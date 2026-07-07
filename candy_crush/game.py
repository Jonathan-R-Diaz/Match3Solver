from candy_crush.board import Board, POWERUPS
from typing import List


class Game:
    def __init__(self, rows=8, cols=8, max_moves=30, seed=0, board_state: List[List[str]] = None, debug=False):
        self.num_candies = None
        self.max_moves = max_moves
        self.moves_left = max_moves
        self.seed = seed
        self.score = 0
        self.debug = debug

        if board_state:
            print("Custom board loaded")
            self.board = Board(board_state=board_state, debug=debug)
            self.rows = len(board_state)
            self.cols = len(board_state[0])
            self.board.print_board()
        else:
            self.rows = rows
            self.cols = cols
            self.reset()

        print("=== Terminal Candy Crush ===")
        print("Match 3 or more candies.")
        print("Enter moves as: row col direction")
        print("Directions: w=up, s=down, a=left, d=right")
        print("Type 'q' to quit.\n")

    def reset(self):
        self.board = Board(
            rows=self.rows,
            cols=self.cols,
            seed=self.seed,
            debug=self.debug
        )
        self.score = 0
        self.moves_left = self.max_moves
        return self.board.get_board()

    def step(self, move: tuple, animate: bool = False):
        """
        move = (r1, c1, d)
        Returns:
            observation, reward, done, info
        """
        if self.is_over():
            raise RuntimeError("Game is already over.")

        info = {
            "score": self.score,
            "moves_left": self.moves_left,
            "valid_moves": self.board.valid_moves(),
        }

        #print("[debug] Move:", move)
        r, c, d = move
        if not self.board.is_valid_move(r, c, d):
            print("That move does not create a match.")
            return self.board.get_board(), 0, self.is_over(), info
            

        r2, c2 = self.board.get_neighbor(r, c, d)
        power_pops = 0
        swapped_powerup_pos = None
        pre_crush_powerups = None
        if self.board.board[r][c] in POWERUPS:
            power_pops += self.board.activate_powerup(r, c, r2, c2)
            self.board.drop()
            self.board.fill()
        else:
            self.board.swap(r, c, r2, c2)
            if self.board.board[r][c] in POWERUPS:
                swapped_powerup_pos = (r, c)
                pre_crush_powerups = {
                    (rr, cc)
                    for rr in range(self.rows)
                    for cc in range(self.cols)
                    if self.board.board[rr][cc] in POWERUPS
                }

        self.board.last_move = ((r, c), (r2, c2))

        if animate:
            crushed, frames = self.board.crush(return_frames=True)
            try:
                from candy_crush.render import animate_frames

                animate_frames(frames)
            except Exception:
                pass
        else:
            crushed = self.board.crush()

        if swapped_powerup_pos:
            sr, sc = swapped_powerup_pos
            if self.board.board[sr][sc] in POWERUPS:
                new_powerups = {
                    (rr, cc)
                    for rr in range(self.rows)
                    for cc in range(self.cols)
                    if self.board.board[rr][cc] in POWERUPS
                    and (rr, cc) not in pre_crush_powerups
                    and not (rr == sr and cc == sc)
                }
                power_pops += self.board.activate_powerup(sr, sc, sr, sc, protected=new_powerups)
                self.board.drop()
                self.board.fill()

        # Score is number of candies crushed (tests rely on reward magnitude)
        self.score += crushed + power_pops
        self.moves_left -= 1

        total = crushed + power_pops
        print(f"Crushed {total} candies!")

        done = self.is_over()

        info = {
            "score": self.score,
            "moves_left": self.moves_left,
            "valid_moves": self.board.valid_moves(),
        }

        return self.board.get_board(), total, done, info

    def is_over(self):
        return (
            self.moves_left <= 0
            or self.board.valid_moves() == 0
        )
    
    def render(self):
        # Use the package renderer if available for colored output, otherwise fall back
        try:
            from candy_crush.render import render_board

            render_board(self.board.get_board(), score=self.score)
        except Exception:
            # Fallback to simple text output
            self.board.print_board(self.score)