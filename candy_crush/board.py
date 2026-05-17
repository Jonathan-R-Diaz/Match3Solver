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
from collections import List

random.seed(42)

CANDIES = [".", "#", "-", "@", "*"]

class Board:
    
    def __init__(self, rows=30, cols=30) -> List[List[str]]:
        """Generate a board with no initial matches."""
        self.rows = rows
        self.cols = cols

        while True:
            self.board = [
                [random.choice(CANDIES) for _ in range(cols)]
                for _ in range(rows)
            ]
            if not self.find_matches(self.board):
                return self.board


    def print_board(self, score):
        print("\n   " + " ".join(str(c) for c in range(self.cols)))
        print("  +" + "--" * self.cols + "+")
        for r in range(self.rows):
            print(f"{r} |" + " ".join(board[r]) + "|")
        print("  +" + "--" * self.cols + "+")
        print(f"Score: {score}\n")


    def in_bounds(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols


    def swap(self, r1, c1, r2, c2):
        self.board[r1][c1], self.board[r2][c2] = self.board[r2][c2], self.board[r1][c1]


    def get_neighbor(self, r, c, direction):
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
        total_crushed = 0

        while True:
            matches = self.find_matches(self.board)
            if not matches:
                break

            total_crushed += len(matches)

            # Remove matched candies
            for r, c in matches:
                self.board[r][c] = " "

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

        return total_crushed


    def is_valid_move(self, r, c, direction):
        neighbor = self.get_neighbor(r, c, direction)
        if neighbor is None:
            return False

        r2, c2 = neighbor
        if not self.in_bounds(r, c) or not self.in_bounds(r2, c2):
            return False

        # Test swap
        self.swap(self.board, r, c, r2, c2)
        valid = bool(self.find_matches(self.board))
        self.swap(self.board, r, c, r2, c2)

        return valid


    def has_possible_moves(self):
        for r in range(self.rows):
            for c in range(self.cols):
                for d in ["w", "a", "s", "d"]:
                    if self.is_valid_move(r, c, d):
                        return True
        return False


    def reshuffle(self):
        candies = [cell for row in self.board for cell in row]
        while True:
            random.shuffle(candies)
            for i in range(self.rows * self.cols):
                self.board[i // self.cols][i % self.cols] = candies[i]
            if not self.find_matches() and self.has_possible_moves():
                return


def main():
    board = Board()
    while not board.has_possible_moves():
        board.reshuffle()

    score = 0

    print("=== Terminal Candy Crush ===")
    print("Match 3 or more candies.")
    print("Enter moves as: row col direction")
    print("Directions: w=up, s=down, a=left, d=right")
    print("Type 'q' to quit.\n")

    while True:
        board.print_board(score)

        if not board.has_possible_moves(board):
            print("No possible moves left. Reshuffling...")
            board.reshuffle()

        move = input("Your move: ").strip().lower()

        if move == "q":
            print(f"Final Score: {score}")
            print("Thanks for playing!")
            break

        parts = move.split()
        if len(parts) != 3:
            print("Invalid input. Example: 3 4 d")
            continue

        try:
            r = int(parts[0])
            c = int(parts[1])
            direction = parts[2]
        except ValueError:
            print("Row and column must be numbers.")
            continue

        if not board.is_valid_move(r, c, direction):
            print("That move does not create a match.")
            continue

        r2, c2 = board.get_neighbor(r, c, direction)
        board.swap(r, c, r2, c2)

        crushed = board.crush(board)
        score += crushed * 10

        print(f"Crushed {crushed} candies!")

if __name__ == "__main__":
    main()
