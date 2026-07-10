from argparse import ArgumentParser
from candy_crush.game import Game
from candy_crush.levels import get_level
from typing import List


def main(board: List[List[str]] = None):
    parser = ArgumentParser()
    parser.add_argument('--animate', action='store_true', help='Enable terminal animation for crushes')
    parser.add_argument('--slomo', action='store_true',
                        help='Step through labeled frames one Enter-press at a time (implies --animate)')
    parser.add_argument('--level', type=int, help='Play a level from candy_crush/levels.py')
    parser.add_argument('--seed', type=int, default=6, help='RNG seed for the candy deal')
    args = parser.parse_args()

    if board is None and args.level is not None:
        board = get_level(args.level)

    if board:
        game = Game(board_state=board, seed=args.seed, fill_empty=True)
    else:
        game = Game(seed=args.seed)

    while True:
        game.render()

        move = input("Your move: ")

        if move.strip() == "q":
            print(f"Final Score: {game.score}")
            game.print_move_history()
            print("Thanks for playing!")
            break

        parts = move.split()
        if len(parts) != 3:
            print("Invalid input. Enter: row col direction")
            continue

        r_str, c_str, d = parts
        try:
            r = int(r_str)
            c = int(c_str)
        except ValueError:
            print("Row and column must be integers.")
            continue

        obs, reward, done, info = game.step((r, c, d),
                                            animate=args.animate or args.slomo,
                                            step_mode=args.slomo)
        #print(f"[debug] obs: {obs} \nreward: {reward} \ndone: {done} \ninfo: {info}")

        if done:
            print("Game over!")
            game.print_move_history()
            break


if __name__ == "__main__":
    main()