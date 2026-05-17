
from candy_crush.game import Game

def main():
    
    game = Game()
    game.reset()

    while True:
        game.render()

        move = input("Your move: ")

        if move == "q":
            print(f"Final Score: {game.score}")
            print("Thanks for playing!")
            break

        r, c, d = move.split()
        r, c = int(r), int(c)

        obs, reward, done, info = game.step((int(r), int(c), d))
        print(f"[debug] obs: {obs} \nreward: {reward} \ndone: {done} \ninfo: {info}")

        if done:
            print("Game over!")
            break


if __name__ == "__main__":
    main()