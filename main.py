import pygame
from menu import Menu
from game import Game

def main():
    pygame.init()
    WIDTH, HEIGHT = 800, 600

    running = True
    current_screen = "menu"

    while running:
        if current_screen == "menu":
            menu = Menu(WIDTH, HEIGHT)
            current_screen = menu.run()
        elif current_screen == "practice":
            game = Game()
            current_screen = game.run()
        elif current_screen == "quit":
            running = False
        elif current_screen == "ai":
            print("AI mode not implemented yet")
            current_screen = "menu"
        elif current_screen == "online":
            print("Online mode not implemented yet")
            current_screen = "menu"

    pygame.quit()

if __name__ == "__main__":
    main()
