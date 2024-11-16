import pygame
from menu import Menu
from game import Game
from online_game import OnlineGame

def main():
    pygame.init()
    WIDTH, HEIGHT = 800, 600

    running = True
    current_screen = "menu"
    game_connection = None

    while running:
        if current_screen == "menu":
            menu = Menu(WIDTH, HEIGHT)
            result = menu.run()
            if isinstance(result, tuple):
                current_screen, game_connection = result
            else:
                current_screen = result
        elif current_screen == "practice":
            game = Game()
            current_screen = game.run()
        elif current_screen == "quit":
            running = False
        elif current_screen == "ai":
            game = Game(mode="ai")
            current_screen = game.run()
        elif current_screen == "online":
            if game_connection and game_connection.is_match_found():
                game = OnlineGame(game_connection)
                current_screen = game.run()
            else:
                print("Error: No valid game connection")
                current_screen = "menu"

    pygame.quit()


if __name__ == "__main__":
    main()
