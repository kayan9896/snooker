import pygame
from menu import Menu
from game import Game

def main():
    pygame.init()
    WIDTH, HEIGHT = 800, 400

    menu = Menu(WIDTH, HEIGHT)
    selected_mode = menu.run()

    if selected_mode == "practice":
        game = Game()
        game.run()
    elif selected_mode == "ai":
        print("AI mode not implemented yet")
    elif selected_mode == "online":
        print("Online mode not implemented yet")

if __name__ == "__main__":
    main()
