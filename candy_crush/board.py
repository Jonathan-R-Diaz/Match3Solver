# terminal_candy_crush.py
# A simple playable Candy Crush-style game for the terminal.
# Controls:
#   Enter moves as: row col direction
#   Directions: w = up, s = down, a = left, d = right
# Example:
#   3 4 d
#
# Goal:
#   Make matches of 3 or more identical candies horizontally or vertically.
#   Matched candies are removed, candies above fall down, and new candies appear.

import random
from collections import defaultdict
from typing import List

CANDIES  = ["r", "b", "g", "y"]
POWERUPS = frozenset({"5", "V", "H", "T", "S"})
ROCKETS  = frozenset({"V", "H"})

class Board:
    
    def __init__(self, rows=5, cols=5, seed=0, board_state: List[List[str]] = None, debug = False):
        """Generate a board with no initial matches."""
        random.seed(seed)
        self.last_move = None
        self.debug = debug
        self._drop_toggle = False
        self.record_frames = False
        self.frames = []
        if board_state:
            self.board = board_state
            self.rows = len(self.board)
            self.cols = len(self.board[0])
        else:
            self.rows = rows
            self.cols = cols
            while True:
                self.board = [
                    [random.choice(CANDIES) for _ in range(cols)]
                    for _ in range(rows)
                ]
                if not self.find_matches(place_powerups=False):
                    break


    def get_board(self):
        return self.board


    def copy(self):
        new_board = Board(self.rows, self.cols)
        new_board.board = [row.copy() for row in self.board]
        return new_board
    

    def simulate_move(self, r, c, direction, revert=True) -> int:
        if revert:
            previous_board = [row.copy() for row in self.board]
        neighbor = self.get_neighbor(r, c, direction)
        if neighbor is None:
            return None

        r2, c2 = neighbor
        if not self.in_bounds(r, c) or not self.in_bounds(r2, c2):
            return None

        crush_count = 0
        if self.board[r][c] in POWERUPS:
            crush_count += self.activate_powerup(r, c, r2, c2)
            self.drop()
        else:
            self.swap(r, c, r2, c2)
        crush_count += self.crush(return_frames=False, refill=False)
        if revert:
            self.board = previous_board

        return crush_count


    def _snap(self):
        """Record a board snapshot while frame recording is on (skips duplicates)."""
        if not self.record_frames:
            return
        frame = [row.copy() for row in self.board]
        if not self.frames or self.frames[-1] != frame:
            self.frames.append(frame)

    def activate_powerup(self, r1: int, c1: int, r2: int, c2: int, protected=None):
        print("[Debug] Activating powerup", r1, c1, r2, c2)
        self._snap()   # board state with this powerup about to fire
        if protected is None:
            protected = set()
        crushed = 0

        # TNT + TNT combo: double-radius blast
        if self.board[r1][c1] == "T" and self.board[r2][c2] == "T" and not (r1 == r2 and c1 == c2):
            self.board[r1][c1] = " "
            self.board[r2][c2] = " "
            crushed += self.clear_area(r1, c1, radius=4)
            return crushed

        # Rocket + Rocket combo: fire a + (row + col) from the target cell
        if self.board[r1][c1] in ROCKETS and self.board[r2][c2] in ROCKETS and not (r1 == r2 and c1 == c2):
            self.board[r1][c1] = " "
            self.board[r2][c2] = " "
            crushed += self.clear_row(r2)
            crushed += self.clear_col(c2)
            return crushed

        # Rocket + TNT combo: fire 3 rows + 3 cols centered on the target cell
        rkt_tnt = (self.board[r1][c1] in ROCKETS and self.board[r2][c2] == "T") or \
                  (self.board[r2][c2] in ROCKETS and self.board[r1][c1] == "T")
        if rkt_tnt and not (r1 == r2 and c1 == c2):
            self.board[r1][c1] = " "
            self.board[r2][c2] = " "
            for r in range(r2 - 1, r2 + 2):
                if self.in_bounds(r, 0):
                    crushed += self.clear_row(r)
            for c in range(c2 - 1, c2 + 2):
                if self.in_bounds(0, c):
                    crushed += self.clear_col(c)
            return crushed

        # EB + EB → clear entire board
        if self.board[r1][c1] == "5" and self.board[r2][c2] == "5" and not (r1 == r2 and c1 == c2):
            self.board[r1][c1] = " "
            self.board[r2][c2] = " "
            for r in range(self.rows):
                for c in range(self.cols):
                    if self.board[r][c] in POWERUPS:
                        crushed += self.activate_powerup(r, c, r, c)
                    elif self.board[r][c] != " ":
                        self.board[r][c] = " "
                        crushed += 1
            return crushed

        # EB + Rocket → replace most common candy with that rocket type, fire each
        eb_rocket = (self.board[r1][c1] == "5" and self.board[r2][c2] in ROCKETS) or \
                    (self.board[r2][c2] == "5" and self.board[r1][c1] in ROCKETS)
        if eb_rocket and not (r1 == r2 and c1 == c2):
            rkt = self.board[r1][c1] if self.board[r1][c1] in ROCKETS else self.board[r2][c2]
            self.board[r1][c1] = " "
            self.board[r2][c2] = " "
            target = self.get_most_candy()
            positions = [(r, c) for r in range(self.rows) for c in range(self.cols) if self.board[r][c] == target]
            for r, c in positions:
                self.board[r][c] = rkt
            for r, c in positions:
                crushed += self.activate_powerup(r, c, r, c)
            return crushed

        # EB + TNT → replace most common candy with TNTs, fire each
        eb_tnt = (self.board[r1][c1] == "5" and self.board[r2][c2] == "T") or \
                 (self.board[r2][c2] == "5" and self.board[r1][c1] == "T")
        if eb_tnt and not (r1 == r2 and c1 == c2):
            self.board[r1][c1] = " "
            self.board[r2][c2] = " "
            target = self.get_most_candy()
            positions = [(r, c) for r in range(self.rows) for c in range(self.cols) if self.board[r][c] == target]
            for r, c in positions:
                self.board[r][c] = "T"
            for r, c in positions:
                crushed += self.activate_powerup(r, c, r, c)
            return crushed

        # EB + Spinner → replace most common candy with Spinners, fire each
        eb_spinner = (self.board[r1][c1] == "5" and self.board[r2][c2] == "S") or \
                     (self.board[r2][c2] == "5" and self.board[r1][c1] == "S")
        if eb_spinner and not (r1 == r2 and c1 == c2):
            self.board[r1][c1] = " "
            self.board[r2][c2] = " "
            target = self.get_most_candy()
            positions = [(r, c) for r in range(self.rows) for c in range(self.cols) if self.board[r][c] == target]
            for r, c in positions:
                self.board[r][c] = "S"
            for r, c in positions:
                self.board[r][c] = " "
                crushed += self.fire_spinner(r, c, chain=False)
            return crushed

        # Spinner + TNT → fire TNT from position that maximizes obstacles cleared
        spinner_tnt = (self.board[r1][c1] == "S" and self.board[r2][c2] == "T") or \
                      (self.board[r2][c2] == "S" and self.board[r1][c1] == "T")
        if spinner_tnt and not (r1 == r2 and c1 == c2):
            self.board[r1][c1] = " "
            self.board[r2][c2] = " "
            best_r, best_c = max(
                ((r, c) for r in range(self.rows) for c in range(self.cols)),
                key=lambda rc: sum(
                    1 for dr in range(-2, 3) for dc in range(-2, 3)
                    if self.in_bounds(rc[0]+dr, rc[1]+dc)
                    and self.board[rc[0]+dr][rc[1]+dc] == 'B'
                )
            )
            crushed += self.clear_area(best_r, best_c)
            return crushed

        # Spinner + Rocket → fire rocket along row/col with most obstacles
        spinner_rocket = (self.board[r1][c1] == "S" and self.board[r2][c2] in ROCKETS) or \
                         (self.board[r2][c2] == "S" and self.board[r1][c1] in ROCKETS)
        if spinner_rocket and not (r1 == r2 and c1 == c2):
            rkt = self.board[r1][c1] if self.board[r1][c1] in ROCKETS else self.board[r2][c2]
            self.board[r1][c1] = " "
            self.board[r2][c2] = " "
            if rkt == 'H':
                best_r = max(range(self.rows),
                             key=lambda r: sum(1 for c in range(self.cols) if self.board[r][c] == 'B'))
                crushed += self.clear_row(best_r)
            else:
                best_c = max(range(self.cols),
                             key=lambda c: sum(1 for r in range(self.rows) if self.board[r][c] == 'B'))
                crushed += self.clear_col(best_c)
            return crushed

        # Spinner + Spinner → fire both spinners, then spawn + fire one extra anywhere
        if self.board[r1][c1] == "S" and self.board[r2][c2] == "S" and not (r1 == r2 and c1 == c2):
            self.board[r1][c1] = " "
            self.board[r2][c2] = " "
            crushed += self.fire_spinner(r1, c1)
            crushed += self.fire_spinner(r2, c2)
            obstacles = [(r, c) for r in range(self.rows) for c in range(self.cols)
                         if self.board[r][c] == 'B']
            if obstacles:
                er, ec = random.choice(obstacles)
                self.board[er][ec] = " "
                crushed += 1
            return crushed

        if self.board[r2][c2] in ("V", "H", "T", "S"):
            r1, c1 = r2, c2
        if self.board[r1][c1] == "H":
            self.board[r1][c1] = " "
            crushed += self.clear_row(r1, protected=protected)
        elif self.board[r1][c1] == "V":
            self.board[r1][c1] = " "
            crushed += self.clear_col(c1, protected=protected)
        elif self.board[r1][c1] == "T":
            self.board[r1][c1] = " "
            crushed += self.clear_area(r1, c1, protected=protected)
        elif self.board[r1][c1] == "S":
            self.board[r1][c1] = " "
            crushed += self.fire_spinner(r1, c1, protected=protected)
        elif r1 == r2 and c1 == c2 and self.board[r1][c1] == "5":
            crushed = self.clear_candies(self.get_most_candy())
        elif self.board[r1][c1] == "5" or self.board[r2][c2] == "5":
            crushed = self.clear_candies(self.board[r2][c2])

        self.board[r1][c1] = " "
        return crushed


    def fire_spinner(self, r: int, c: int, chain: bool = True, protected=None) -> int:
        """Pop the 4 cardinal neighbours, then clear one random obstacle ('B').

        chain=False: powerup neighbors are cleared without triggering their effect
        (used by EB+Spinner so the mass-spawned spinners don't cascade).
        protected: cells to leave completely untouched (e.g. a powerup created
        by the same swap that fired this spinner).
        """
        if protected is None:
            protected = set()
        crushed = 0
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            if not self.in_bounds(nr, nc):
                continue
            if (nr, nc) in protected:
                continue
            if self.board[nr][nc] in POWERUPS:
                if chain:
                    crushed += self.activate_powerup(nr, nc, nr, nc)
                # chain=False: skip powerups entirely — they stay on the board
            elif self.board[nr][nc] not in (' ', '#'):
                self.board[nr][nc] = ' '
                crushed += 1
        obstacles = [(rr, cc) for rr in range(self.rows) for cc in range(self.cols)
                     if self.board[rr][cc] == 'B']
        if obstacles:
            rr, cc = random.choice(obstacles)
            self.board[rr][cc] = ' '
            crushed += 1
        self._snap()
        return crushed


    def get_most_candy(self):
        freq = defaultdict(int)
        most_freq = -1
        most_candy = None
        for row in self.board:
            for c in row:
                freq[c] += 1
                if freq[c] > most_freq:
                    most_freq = freq[c]
                    most_candy = c
        
        assert most_candy, "Most candy is None"
        return most_candy
            

    def clear_candies(self, candy, drop=True):
        crushed = 0
        for row in self.board:
            for i in range(self.cols):
                if row[i] == candy:
                    row[i] = " "
                    crushed += 1
        if drop:
            self.drop()
        
        return crushed


    def clear_area(self, r, c, radius=2, protected=None):
        if protected is None:
            protected = set()
        crushed = 0
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                nr, nc = r + dr, c + dc
                if not self.in_bounds(nr, nc):
                    continue
                if (nr, nc) in protected:
                    continue
                if self.board[nr][nc] in ['V', 'H', '5', 'T']:
                    crushed += self.activate_powerup(nr, nc, nr, nc)
                elif self.board[nr][nc] not in (' ', '#'):
                    self.board[nr][nc] = ' '
                    crushed += 1
        self._snap()
        return crushed


    def clear_col(self, c, protected=None):
        if protected is None:
            protected = set()
        crushed = 0
        for i in range(self.rows):
            if (i, c) in protected:
                continue
            if self.board[i][c] in POWERUPS:
                crushed += self.activate_powerup(i, c, i, c)
            if self.board[i][c] not in (' ', '#'):
                self.board[i][c] = " "
                crushed += 1

        self._snap()
        return crushed


    def clear_row(self, r, protected=None):
        if protected is None:
            protected = set()
        crushed = 0
        for j in range(self.cols):
            if (r, j) in protected:
                continue
            if self.board[r][j] in POWERUPS:
                crushed += self.activate_powerup(r, j, r, j)
            if self.board[r][j] not in (' ', '#'):
                self.board[r][j] = " "
                crushed += 1

        self._snap()
        return crushed


    def print_board(self, score = -1):
        print("\n    " + " ".join(str(c) for c in range(self.cols)))
        print("  +" + "--" * self.cols + "-+")
        for r in range(self.rows):
            print(f"{r} | " + " ".join(self.board[r]) + " |")
        print("  +" + "--" * self.cols + "-+")
        print(f"Score: {score}\n")


    def in_bounds(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols


    def swap(self, r1, c1, r2, c2):
        self.board[r1][c1], self.board[r2][c2] = self.board[r2][c2], self.board[r1][c1]


    def get_neighbor(self, r: int, c: int, direction: str):
        moves = {
            "w": (-1, 0),
            "s": (1, 0),
            "a": (0, -1),
            "d": (0, 1),
            "x": (0, 0)
        }
        if direction not in moves:
            return None
        dr, dc = moves[direction]
        nr, nc = r + dr, c + dc
        if nr < 0 or nc < 0 or nr >= self.rows or nc >= self.cols:
            return None
        return nr, nc


    def positioned_for_upgrade(self, r, c):
        return  self.last_move \
        and ((r == self.last_move[0][0] and c == self.last_move[0][1]) \
        or  (r == self.last_move[1][0] and c == self.last_move[1][1]))


    def find_matches(self, place_powerups: bool = True) -> set:
        """Return a set of (row, col) positions that are part of matches."""

        #TODO: Randomize where the powerup gets placed if it was part of a cascade

        matched = set()
        h_three = set()  # cells in exactly-3 horizontal runs
        v_three = set()  # cells in exactly-3 vertical runs
        h_fours = []     # 4-runs (list of cell lists); rocket unless crossed → TNT
        v_fours = []
        self.rows = len(self.board)
        self.cols = len(self.board[0])

        # Horizontal matches
        for r in range(self.rows):
            count = 1
            for c in range(self.cols - 1):
                if self.board[r][c] == self.board[r][c + 1] and self.board[r][c] not in (" ", "#", "B"):
                    count += 1

                if self.board[r][c] != self.board[r][c + 1] or c == self.cols - 2:

                    if self.board[r][c] == self.board[r][c + 1] and c == self.cols - 2:
                        c += 1
                    if count >= 3:
                        for k in range(c - count + 1, c + 1):
                            matched.add((r, k))
                    if count == 3:
                        for k in range(c - count + 1, c + 1):
                            h_three.add((r, k))
                    if count == 4:
                        h_fours.append([(r, k) for k in range(c - count + 1, c + 1)])
                    if place_powerups and count >= 5:
                        candy = 0
                        for k in range(c - count + 1, c + 1):
                            candy += 1
                            if candy == 3:
                                self.board[r][k] = "5"
                    count = 1


        # Vertical matches
        for c in range(self.cols):
            count = 1
            for r in range(self.rows - 1):
                if self.board[r][c] == self.board[r + 1][c] and self.board[r][c] not in (" ", "#", "B"):
                    count += 1

                if self.board[r][c] != self.board[r + 1][c] or r == self.rows - 2:
                    if self.board[r][c] == self.board[r + 1][c] and r == self.rows - 2:
                        r += 1
                    if count >= 3:
                        for k in range(r - count + 1, r + 1):
                            matched.add((k, c))
                    if count == 3:
                        for k in range(r - count + 1, r + 1):
                            v_three.add((k, c))
                    if count == 4:
                        v_fours.append([(k, c) for k in range(r - count + 1, r + 1)])
                    if place_powerups and count >= 5:
                        candy = 0
                        for k in range(self.rows - count, self.rows):
                            candy += 1
                            if candy == 3:
                                self.board[k][c] = "5"
                    count = 1

        if place_powerups:
            # TNT wins any horizontal x vertical crossing (3- or 4-runs alike);
            # 4-runs consumed by a TNT do not also spawn a rocket.
            h_line_cells = h_three | {cell for run in h_fours for cell in run}
            v_line_cells = v_three | {cell for run in v_fours for cell in run}
            tnt_spots = h_line_cells & v_line_cells
            for (r, c) in tnt_spots:
                self.board[r][c] = "T"
            for run in h_fours + v_fours:
                if any(cell in tnt_spots for cell in run):
                    continue
                rr, rc = next((p for p in run if self.positioned_for_upgrade(*p)), run[2])
                self.board[rr][rc] = self.random_rocket()

        # 2x2 square of same candy → Spinner
        # Runs after line powerups: an already-upgraded cell breaks the square's
        # equality, so rockets/EBs/TNTs take priority over the spinner.
        for r in range(self.rows - 1):
            for c in range(self.cols - 1):
                cell = self.board[r][c]
                if cell not in CANDIES:
                    continue
                if (self.board[r][c + 1] == cell
                        and self.board[r + 1][c] == cell
                        and self.board[r + 1][c + 1] == cell):
                    square = [(r, c), (r, c + 1), (r + 1, c), (r + 1, c + 1)]
                    matched.update(square)
                    if place_powerups:
                        sr, sc = next((p for p in square if self.positioned_for_upgrade(*p)),
                                      (r, c))
                        self.board[sr][sc] = "S"

        return matched
    

    def pop(self) -> int:
        matches = self.find_matches()
        if not matches:
            return 0

        # Remove matched candies
        for r, c in matches:
            if self.board[r][c] not in POWERUPS:
                self.board[r][c] = " "

        # Each matched cell hits adjacent boxes
        box_pops = set()
        for r, c in matches:
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nr, nc = r + dr, c + dc
                if self.in_bounds(nr, nc) and self.board[nr][nc] == "B":
                    box_pops.add((nr, nc))
        for r, c in box_pops:
            self.board[r][c] = " "

        self._snap()
        return len(matches) + len(box_pops)
            

    def drop(self):
        changed = True
        while changed:
            changed = False
            for r in range(self.rows - 2, -1, -1):
                for c in range(self.cols):
                    cell = self.board[r][c]
                    if cell in (' ', '#', 'B'):
                        continue
                    if self.board[r + 1][c] == ' ':
                        self.board[r + 1][c] = cell
                        self.board[r][c] = ' '
                        changed = True
        self._snap()


    def fill(self, fill_with=None):
        center = self.cols // 2
        while True:
            falling = set()
            for c in range(self.cols):
                if self.board[0][c] == ' ':
                    self.board[0][c] = fill_with if fill_with is not None else random.choice(CANDIES)
                    falling.add((0, c))
            if not falling:
                break
            while falling:
                new_falling = set()
                for r in range(self.rows - 2, -1, -1):
                    for c in range(self.cols):
                        if (r, c) not in falling:
                            continue
                        cell = self.board[r][c]
                        if self.board[r + 1][c] == ' ':
                            self.board[r + 1][c] = cell
                            self.board[r][c] = ' '
                            new_falling.add((r + 1, c))
                            continue
                        below_left = self.in_bounds(r + 1, c - 1) and self.board[r + 1][c - 1] == ' '
                        below_right = self.in_bounds(r + 1, c + 1) and self.board[r + 1][c + 1] == ' '
                        if below_left and below_right:
                            if c < center:
                                nc = c - 1
                            elif c > center:
                                nc = c + 1
                            else:
                                nc = c - 1 if self._drop_toggle else c + 1
                                self._drop_toggle = not self._drop_toggle
                        elif below_left:
                            nc = c - 1
                        elif below_right:
                            nc = c + 1
                        else:
                            continue
                        self.board[r + 1][nc] = cell
                        self.board[r][c] = ' '
                        new_falling.add((r + 1, nc))
                falling = new_falling
        self._snap()


    def crush(self, return_frames: bool = False, refill: bool = True):
        """
        Repeatedly find matches, remove them, drop candies and refill.
        If return_frames is True, also collect intermediate board snapshots (frames)
        and return (total_crushed, frames). Otherwise just return total_crushed (int).
        """
        total_crushed = 0
        frames = []

        while True:
            # Capture before-removal state
            if return_frames:
                frames.append([row.copy() for row in self.board])
            
            pops = self.pop()
            total_crushed += pops
            if pops == 0:
                break
            
            # Capture after-removal (empty spots)
            if return_frames:
                frames.append([row.copy() for row in self.board])
            
            self.drop()
            if refill:       
                self.fill()
            
            # Capture after refill
            if return_frames:
                frames.append([row.copy() for row in self.board])

        if return_frames:
            return total_crushed, frames
        return total_crushed


    def is_valid_move(self, r, c, direction):
        if self.board[r][c] in (' ', '#', 'B'):
            return False
        if self.board[r][c] in POWERUPS:
            return self.get_neighbor(r, c, direction) is not None

        neighbor = self.get_neighbor(r, c, direction)
        if neighbor is None:
            return False

        r2, c2 = neighbor
        if not self.in_bounds(r, c) or not self.in_bounds(r2, c2):
            return False

        # Test swap
        self.swap(r, c, r2, c2)
        valid = bool(self.find_matches(place_powerups=False))
        self.swap(r, c, r2, c2)

        return valid


    def has_possible_moves(self):
        for r in range(self.rows):
            for c in range(self.cols):
                for d in ["w", "a", "s", "d"]:
                    if self.is_valid_move(r, c, d):
                        return True
        return False


    def valid_moves(self) -> int:
        moves = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] in POWERUPS:
                    moves.append((r,c,"x"))
                for d in ["w", "a", "s", "d"]:
                    if self.is_valid_move(r, c, d):
                        moves.append((r,c,d))
        return moves


    def reshuffle(self):
        candies = [cell for row in self.board for cell in row]
        while True:
            random.shuffle(candies)
            for i in range(self.rows * self.cols):
                self.board[i // self.cols][i % self.cols] = candies[i]
            if not self.find_matches() and self.has_possible_moves():
                return


    def random_rocket(self):
        heads = random.choice([True, False])
        if self.debug or heads:
            return "H"

        return "V"