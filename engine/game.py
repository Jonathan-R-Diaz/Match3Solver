from engine.board import Board, POWERUPS
from typing import List
from collections import defaultdict


OBSTACLES = { "B" }

class Game:
    def __init__(self, rows=8, cols=8, max_moves=30, seed=0, board_state: List[List[str]] = None, debug=False, fill_empty=False, freeplay=True, verbose=True):
        self.num_candies = None
        self.verbose = verbose
        self.max_moves = max_moves
        self.moves_left = max_moves
        self.seed = seed
        self.score = 0
        self.debug = debug
        self.move_history = []
        # level template: layout whose ' ' cells get dealt random candies
        self.template = board_state if fill_empty else None
        self.fill_empty = fill_empty
        self.freeplay = freeplay

        if board_state:
            state = [row.copy() for row in board_state] if fill_empty else board_state
            self.board = Board(board_state=state, seed=seed, debug=debug, fill_empty=fill_empty)
            self.rows = len(board_state)
            self.cols = len(board_state[0])
            if self.verbose:
                print("Custom board loaded")
                self.board.print_board()
            self.initial_board = [row.copy() for row in self.board.grid]
        else:
            self.rows = rows
            self.cols = cols
            self.reset()


    def reset(self):
        if self.template:
            self.board = Board(
                board_state=[row.copy() for row in self.template],
                seed=self.seed,
                debug=self.debug,
                fill_empty=True,
            )
        else:
            self.board = Board(
                rows=self.rows,
                cols=self.cols,
                seed=self.seed,
                debug=self.debug
            )
        self.score = 0
        self.moves_left = self.max_moves
        self.move_history = []
        self.initial_board = [row.copy() for row in self.board.grid]
        return self.board.get_board()


    def step(self, move: tuple, animate: bool = False, step_mode: bool = False):
        """
        move = (r1, c1, d)
        Returns:
            observation, reward, done, info
        """
        if self.is_over():
            raise RuntimeError("Game is already over.")

        #print("[debug] Move:", move)
        r, c, d = move
        if not self.board.is_valid_move(r, c, d):
            if self.verbose:
                print("That move does not create a match.")
            info = {
                "score": self.score,
                "moves_left": self.moves_left,
                "valid_moves": self.board.valid_moves(),
            }
            return self.board.get_board(), 0, self.is_over(), info

        self.move_history.append((r, c, d))

        if animate:
            self.board.frames = []
            self.board.record_frames = True
            self.board._snap("start")

        r2, c2 = self.board.get_neighbor(r, c, d)
        power_pops = 0
        swapped_powerup_pos = None
        pre_crush_powerups = None
        if self.board.grid[r][c] in POWERUPS and \
           (self.board.grid[r2][c2] in POWERUPS or self.board.grid[r2][c2] in (' ', '#', 'B')):
            # powerup+powerup combo, or nothing swappable behind — fire in place
            power_pops += self.board.activate_powerup(r, c, r2, c2)
            self.board.drop()
            self.board.fill()
        else:
            self.board.swap(r, c, r2, c2)
            self.board._snap("swap")
            # whichever cell now holds a powerup is the one that slid in the swap
            if self.board.grid[r][c] in POWERUPS:
                swapped_powerup_pos = (r, c)
            elif self.board.grid[r2][c2] in POWERUPS:
                swapped_powerup_pos = (r2, c2)
            if swapped_powerup_pos:
                pre_crush_powerups = {
                    (rr, cc)
                    for rr in range(self.rows)
                    for cc in range(self.cols)
                    if self.board.grid[rr][cc] in POWERUPS
                }

        self.board.last_move = ((r, c), (r2, c2))

        if swapped_powerup_pos:
            # Resolve the swap's own match first (this may create new powerups),
            # then fire the swapped powerup immediately — before any gravity or
            # cascades — leaving the freshly created powerups untouched.
            sr, sc = swapped_powerup_pos
            power_pops += self.board.pop()
            if self.board.grid[sr][sc] in POWERUPS:
                new_powerups = {
                    (rr, cc)
                    for rr in range(self.rows)
                    for cc in range(self.cols)
                    if self.board.grid[rr][cc] in POWERUPS
                    and (rr, cc) not in pre_crush_powerups
                    and not (rr == sr and cc == sc)
                }
                power_pops += self.board.activate_powerup(sr, sc, sr, sc, protected=new_powerups)
            self.board.drop()
            self.board.fill()

        crushed = self.board.crush()

        if animate:
            self.board._snap("final")
            self.board.record_frames = False
            try:
                from engine.render import animate_frames

                animate_frames(self.board.frames, step_mode=step_mode)
            except Exception:
                pass

        # Score is number of candies crushed (tests rely on reward magnitude)
        self.score += crushed + power_pops
        self.moves_left -= 1

        total = crushed + power_pops
        if self.verbose:
            print(f"Crushed {total} candies!")

        win_condition = False
        if not self.freeplay:
            if self.verbose:
                print("Not freeplay mode: checking win condition...")
            win_condition = self.board.get_obstacles() == {}
        done = self.is_over() or win_condition

        if self.debug:
            violations = self.board.validate()
            if violations:
                raise AssertionError(
                    "Board invariants violated after step:\n  "
                    + "\n  ".join(violations)
                    + f"\nRepro: seed={self.seed}"
                    + f"\ninitial_board={self.initial_board!r}"
                    + f"\nmove_history={self.move_history!r}"
                )

        info = {
            "score": self.score,
            "moves_left": self.moves_left,
            "valid_moves": self.board.valid_moves(),
        }

        return self.board.get_board(), total, done, info


    def is_over(self):
        return (
            self.moves_left <= 0
            or len(self.board.valid_moves()) == 0
        )  # win condition: no obstacles left


    def print_move_history(self):
        """Dump the executed moves as a paste-able list for replaying a game."""
        print(f"\nMove history ({len(self.move_history)} moves):")
        print(self.move_history)
    

    def render(self):
        # Use the package renderer if available for colored output, otherwise fall back
        try:
            from engine.render import render_board

            render_board(self.board.get_board(), score=self.score, moves_left=self.moves_left, obstacles=self.board.get_obstacles())
        except Exception:
            # Fallback to simple text output
            self.board.print_board(self.score)