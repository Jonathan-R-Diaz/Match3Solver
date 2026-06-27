from argparse import ArgumentParser
from candy_crush.game import Game


def most_pop(game, moves):
    max_crush = 0
    best_move = None
    for move in moves:
        r, c, d = move
        crush_count = game.board.simulate_move(r, c, d)
        if crush_count >= max_crush:
            max_crush = crush_count
            best_move = move
    return best_move


def main():
    parser = ArgumentParser()
    parser.add_argument('--animate', action='store_true', help='Enable terminal animation for crushes')
    args = parser.parse_args()

    game = Game()
    game.reset()

    while True:
        print(("#" * 100 + '\n') * 3)
        game.render()

        moves = game.board.valid_moves()
        r, c, d = most_pop(game, moves)

        _, reward, done, info = game.step((r, c, d), animate=args.animate)
        print(f"reward: {reward} | score: {info['score']} | moves_left: {info['moves_left']}")

        if done:
            print(f"Game over! Final score: {game.score}")
            break


if __name__ == "__main__":
    main()
