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

CANDIES = ["$", "#", "&", "@", "*"]

class Board:
    
    def __init__(self, rows=5, cols=5, seed=0, board_state: List[List[str]] = None):
        """Generate a board with no initial matches."""
        random.seed(seed)
        self.last_move = None
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
                if not self.find_matches():
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

        # Test swap
        self.swap(r, c, r2, c2)
        crush_count = self.crush(return_frames=False, refill=False)
        if revert:
            self.board = previous_board  # revert to original state

        return crush_count


    def activate_powerup(self, r1: int, c1: int, r2: int, c2: int):
        print("Activating powerup on", r1, c1)
        # Power up must be on r1, c1
        if self.board[r1][c1] == "4":
            raise ValueError("lol that shouldnt exist yet")
        if r1 == r2 and c1 == c2:
            crushed = self.clear_candies(self.get_most_candy())
        else:
            crushed = self.clear_candies(self.board[r2][c2])

        self.board[r1][c2] = " "
        print(f"Power-up crushed {crushed} candies!")
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
        
        print(f"Power-up crushed {crushed} '{candy}' candies!")
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
        dr, dc = moves[direction]
        if direction not in moves or r + dr >= self.rows or c + dc >= self.cols:
            return None
        return r + dr, c + dc


    def positioned_for_upgrade(self, r, c):
        return  self.last_move \
        and ((r == self.last_move[0][0] and c == self.last_move[0][1]) \
        or  (r == self.last_move[1][0] and c == self.last_move[1][1]))


    def find_matches(self):
        """Return a set of (row, col) positions that are part of matches."""
        matched = set()
        self.rows = len(self.board)
        self.cols = len(self.board[0])

        # Horizontal matches
        for r in range(self.rows):
            count = 1
            for c in range(self.cols - 1):
                if self.board[r][c] == self.board[r][c + 1] and self.board[r][c] != " ":
                    count += 1

                if self.board[r][c] != self.board[r][c + 1] or c == self.cols - 2:

                    if self.board[r][c] == self.board[r][c + 1] and c == self.cols - 2:
                        c += 1
                    if count >= 3:
                        for k in range(c - count + 1, c + 1):
                            matched.add((r, k))
                    if count == 4:
                        placed = False
                        candy = 0
                        for k in range(c - count + 1, c + 1):
                            candy += 1
                            if self.positioned_for_upgrade(r, k):
                                print("The 4 should be placed on", r, k)
                            if self.positioned_for_upgrade(r, k) \
                            or (candy == 3 and not placed):
                                print("The 4 will be placed on", r, k)
                                self.board[r][k] = "4"
                                placed = True
                    if count >= 5:
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
                if self.board[r][c] == self.board[r + 1][c] and self.board[r][c] != " ":
                    count += 1

                if self.board[r][c] != self.board[r + 1][c] or r == self.rows - 2:
                    if self.board[r][c] == self.board[r + 1][c] and r == self.rows - 2:
                        r += 1
                    if count >= 3:
                        for k in range(r - count + 1, r + 1):
                            matched.add((k, c))
                    if count == 4:
                        placed = False
                        candy = 0
                        for k in range(self.rows - count, self.rows):
                            candy += 1
                            if self.positioned_for_upgrade(k, c) \
                            or (candy == 3 and not placed):
                                self.board[k][c] = "4"
                                placed = True
                    elif count >= 5:
                        candy = 0
                        for k in range(self.rows - count, self.rows):
                            candy += 1
                            if candy == 3: 
                                self.board[k][c] = "5"
                    count = 1

        return matched
    

    def pop(self) -> int:
        matches = self.find_matches()
        if not matches:
            return 0

        # Remove matched candies
        for r, c in matches:
            if self.board[r][c] != "5" and self.board[r][c] != "4":
                self.board[r][c] = " "

        return len(matches)
            

    def drop(self):
        n = len(self.board)
        m = len(self.board[0])

        for i in range(n - 1, -1, -1):
            for j in range(m - 1, -1, -1):
                if self.board[i][j] != " ":
                    continue
                
                k = i - 1
                while k >= 0 and self.board[k][j] == " ":
                    k -= 1    
                offset = i - k
                for k in range(i, -1, -1):
                    if k - offset >= 0:
                        self.board[k][j] = self.board[k - offset][j]
                    else:
                        self.board[k][j] = " "


    def fill(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] == " ":
                    self.board[r][c] = random.choice(CANDIES)


    def crush(self):
        """
        Repeatedly:
        1. Find matches
        2. Remove them
        3. Drop candies
        4. Fill new candies
        Returns the total number of candies crushed.
        """
        return self.crush(return_frames=False)

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
        neighbor = self.get_neighbor(r, c, direction)
        if neighbor is None:
            return False

        r2, c2 = neighbor
        if not self.in_bounds(r, c) or not self.in_bounds(r2, c2):
            return False

        # Test swap
        self.swap(r, c, r2, c2)
        valid = bool(self.find_matches())
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
                if self.board[r][c] in ["4", "5"]:
                    moves.append((r,c,"x"))
                for d in ["w", "a", "s", "d"]:
                    if self.is_valid_move(r, c, d) or self.board[r][c] in ["4", "5"]:
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

