from argparse import ArgumentParser
from candy_crush.game import Game
from typing import List


def main(board: List[List[str]] = None):
    parser = ArgumentParser()
    parser.add_argument('--animate', action='store_true', help='Enable terminal animation for crushes')
    args = parser.parse_args()

    game = Game(board_state=board)

    while True:
        game.render()

        move = input("Your move: ")

        if move.strip() == "q":
            print(f"Final Score: {game.score}")
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

        obs, reward, done, info = game.step((r, c, d), animate=args.animate)
        #print(f"[debug] obs: {obs} \nreward: {reward} \ndone: {done} \ninfo: {info}")

        if done:
            print("Game over!")
            break


if __name__ == "__main__":
    main()