from argparse import ArgumentParser
from candy_crush.game import Game


def pick_first(moves):
    return moves[0]


def pick_last(moves):
    return moves[-1]


def main():
    parser = ArgumentParser()
    parser.add_argument('--animate', action='store_true', help='Enable terminal animation for crushes')
    args = parser.parse_args()

    game = Game()
    game.reset()

    while True:
        print(("#" * 100 + '\n') * 3)
        game.render()

        '''
        move = input("< break :3 > ")

        if moves.strip() == "q":
            print(f"Final Score: {game.score}")
            print("Thanks for playing!")
            break
        '''
        
        moves = game.board.valid_moves()

        parts = most_pop(game, moves)

        r_str, c_str, d = parts
        try:
            r = int(r_str)
            c = int(c_str)
        except ValueError:
            print("Row and column must be integers.")
            continue

        obs, reward, done, info = game.step((r, c, d), animate=args.animate)
        print(f"[debug] obs: {obs} \nreward: {reward} \ndone: {done} \ninfo: {info}")

        if done:
            print("Game over!")
            break


if __name__ == "__main__":
    main()