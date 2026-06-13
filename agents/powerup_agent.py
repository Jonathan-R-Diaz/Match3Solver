"""Agent utilities to detect powerup-forming swaps and pick the best move.

Provides:
- find_matches_on_array(board): returns set of (r,c) that form matches in the given 2D array
- detect_powerup_types(board, matched): detects straight-5, straight-4, T/L shapes
- evaluate_swap(board_obj, r, c, d, weights): score a swap
- choose_best_move(board_obj, weights): enumerate valid swaps and return best (r,c,d)
"""
from typing import List, Set, Tuple, Dict, Optional


def find_matches_on_array(board: List[List[str]]) -> Set[Tuple[int, int]]:
    rows = len(board)
    cols = len(board[0]) if rows > 0 else 0
    matched = set()

    # Horizontal
    for r in range(rows):
        count = 1
        for c in range(1, cols):
            if board[r][c] == board[r][c - 1]:
                count += 1
            else:
                if count >= 3:
                    for k in range(c - count, c):
                        matched.add((r, k))
                count = 1
        if count >= 3:
            for k in range(cols - count, cols):
                matched.add((r, k))

    # Vertical
    for c in range(cols):
        count = 1
        for r in range(1, rows):
            if board[r][c] == board[r - 1][c]:
                count += 1
            else:
                if count >= 3:
                    for k in range(r - count, r):
                        matched.add((k, c))
                count = 1
        if count >= 3:
            for k in range(rows - count, rows):
                matched.add((k, c))

    return matched


def contiguous_run_length(board: List[List[str]], r: int, c: int, dr: int, dc: int) -> int:
    rows = len(board)
    cols = len(board[0]) if rows > 0 else 0
    ch = board[r][c]
    if ch == ' ':
        return 0
    n = 1
    rr, cc = r + dr, c + dc
    while 0 <= rr < rows and 0 <= cc < cols and board[rr][cc] == ch:
        n += 1
        rr += dr
        cc += dc
    rr, cc = r - dr, c - dc
    while 0 <= rr < rows and 0 <= cc < cols and board[rr][cc] == ch:
        n += 1
        rr -= dr
        cc -= dc
    return n


def detect_powerup_types(board: List[List[str]], matched: Set[Tuple[int, int]]) -> Dict[str, bool]:
    types = {"5": False, "4": False, "T": False}
    for (r, c) in matched:
        horiz = contiguous_run_length(board, r, c, 0, 1)
        vert = contiguous_run_length(board, r, c, 1, 0)
        if horiz >= 5 or vert >= 5:
            types["5"] = True
        if horiz >= 4 or vert >= 4:
            types["4"] = True
        if horiz >= 3 and vert >= 3:
            types["T"] = True
    return types


def _board_array_from_obj(board_obj) -> List[List[str]]:
    # Accept either a Board instance with .board or a raw 2D list
    if hasattr(board_obj, 'board'):
        return [row.copy() for row in board_obj.board]
    # assume it's already a 2D list
    return [row.copy() for row in board_obj]


def evaluate_swap(board_obj, r: int, c: int, d: str, weights: Optional[Dict[str, int]] = None) -> Optional[float]:
    if weights is None:
        weights = {"5": 1000, "T": 800, "4": 500, "per_candy": 10}

    rows = len(board_obj.board)
    cols = len(board_obj.board[0])
    # neighbor
    moves = {"w": (-1, 0), "s": (1, 0), "a": (0, -1), "d": (0, 1)}
    if d not in moves:
        return None
    dr, dc = moves[d]
    r2, c2 = r + dr, c + dc
    if not (0 <= r2 < rows and 0 <= c2 < cols):
        return None

    board = _board_array_from_obj(board_obj)
    # simulate swap
    board[r][c], board[r2][c2] = board[r2][c2], board[r][c]

    matched = find_matches_on_array(board)
    if not matched:
        return None

    types = detect_powerup_types(board, matched)
    score = 0.0
    if types.get("5"):
        score += weights["5"]
    if types.get("T"):
        score += weights["T"]
    if types.get("4"):
        score += weights["4"]
    score += len(matched) * weights.get("per_candy", 0)

    return score


def choose_best_move(board_obj, weights: Optional[Dict[str, int]] = None) -> Optional[Tuple[int, int, str, float]]:
    # Enumerate valid swaps using board_obj.is_valid_move to prune
    best = None  # tuple (r,c,d,score)
    rows = len(board_obj.board)
    cols = len(board_obj.board[0])
    for r in range(rows):
        for c in range(cols):
            for d in ["w", "a", "s", "d"]:
                try:
                    if not board_obj.is_valid_move(r, c, d):
                        continue
                except Exception:
                    # If board_obj doesn't have is_valid_move or it errors, still attempt simulation
                    pass

                score = evaluate_swap(board_obj, r, c, d, weights)
                if score is None:
                    continue
                if best is None or score > best[3]:
                    best = (r, c, d, score)
    return best


if __name__ == '__main__':
    print('Run from code: import agents.powerup_agent and call choose_best_move(board)')
