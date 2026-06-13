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


CANDIES = ["$", "#", "&", "@", "*"]

class Board:
    
    def __init__(self, rows=5, cols=5, seed=0):
        """Generate a board with no initial matches."""
        random.seed(seed)
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

    def print_board(self, score):
        print("\n   " + " ".join(str(c) for c in range(self.cols)))
        print("  +" + "--" * self.cols + "+")
        for r in range(self.rows):
            print(f"{r} |" + " ".join(self.board[r]) + "|")
        print("  +" + "--" * self.cols + "+")
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
        }
        if direction not in moves:
            return None
        dr, dc = moves[direction]
        return r + dr, c + dc


    def find_matches(self):
        """Return a set of (row, col) positions that are part of matches."""
        matched = set()

        # Horizontal matches
        for r in range(self.rows):
            count = 1
            for c in range(1, self.cols):
                if self.board[r][c] == self.board[r][c - 1]:
                    count += 1
                else:
                    if count >= 3:
                        for k in range(c - count, c):
                            matched.add((r, k))
                    count = 1
            if count >= 3:
                for k in range(self.cols - count, self.cols):
                    matched.add((r, k))

        # Vertical matches
        for c in range(self.cols):
            count = 1
            for r in range(1, self.rows):
                if self.board[r][c] == self.board[r - 1][c]:
                    count += 1
                else:
                    if count >= 3:
                        for k in range(r - count, r):
                            matched.add((k, c))
                    count = 1
            if count >= 3:
                for k in range(self.rows - count, self.rows):
                    matched.add((k, c))

        return matched


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

    def crush(self, return_frames: bool = False):
        """
        Repeatedly find matches, remove them, drop candies and refill.
        If return_frames is True, also collect intermediate board snapshots (frames)
        and return (total_crushed, frames). Otherwise just return total_crushed (int).
        """
        total_crushed = 0
        frames = []

        while True:
            matches = self.find_matches()
            if not matches:
                break

            total_crushed += len(matches)

            # Capture before-removal state
            if return_frames:
                frames.append([row.copy() for row in self.board])

            # Remove matched candies
            for r, c in matches:
                self.board[r][c] = " "

            # Capture after-removal (empty spots)
            if return_frames:
                frames.append([row.copy() for row in self.board])

            # Drop candies and refill
            for c in range(self.cols):
                remaining = [
                    self.board[r][c]
                    for r in range(self.rows)
                    if self.board[r][c] != " "
                ]
                spaces = self.rows - len(remaining)
                new_column = (
                    [random.choice(CANDIES) for _ in range(spaces)]
                    + remaining
                )

                for r in range(self.rows):
                    self.board[r][c] = new_column[r]

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

