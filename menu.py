import pygame
import sys

class Menu:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Billiards Game")

        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (128, 128, 128)
        self.BLUE = (0, 0, 255)

        # Button dimensions
        self.button_width = 200
        self.button_height = 50
        self.button_margin = 20

        # Initialize font
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 36)

    def draw_button(self, text, y_position, hover=False):
        button_x = (self.screen_width - self.button_width) // 2
        button_color = self.GRAY if hover else self.BLACK

        button_rect = pygame.Rect(button_x, y_position, self.button_width, self.button_height)
        pygame.draw.rect(self.screen, button_color, button_rect)
        pygame.draw.rect(self.screen, self.WHITE, button_rect, 2)

        text_surface = self.small_font.render(text, True, self.WHITE)
        text_rect = text_surface.get_rect(center=button_rect.center)
        self.screen.blit(text_surface, text_rect)

        return button_rect

    def run(self):
        while True:
            # Get mouse position
            mouse_pos = pygame.mouse.get_pos()

            # Clear screen
            self.screen.fill(self.BLUE)

            # Draw title
            title_text = self.font.render("Billiards Game", True, self.WHITE)
            title_rect = title_text.get_rect(center=(self.screen_width//2, 100))
            self.screen.blit(title_text, title_rect)

            # Draw buttons
            practice_button = self.draw_button("Practice Mode", 200, 
                self.is_mouse_over_button(mouse_pos, 200))
            ai_button = self.draw_button("Play Against AI", 280, 
                self.is_mouse_over_button(mouse_pos, 280))
            online_button = self.draw_button("Play Online", 360, 
                self.is_mouse_over_button(mouse_pos, 360))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if practice_button.collidepoint(mouse_pos):
                        return "practice"
                    elif ai_button.collidepoint(mouse_pos):
                        return "ai"
                    elif online_button.collidepoint(mouse_pos):
                        return "online"

            pygame.display.flip()

    def is_mouse_over_button(self, mouse_pos, button_y):
        button_x = (self.screen_width - self.button_width) // 2
        return (button_x <= mouse_pos[0] <= button_x + self.button_width and 
                button_y <= mouse_pos[1] <= button_y + self.button_height)
