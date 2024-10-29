import pygame
import math

class Portal:
    def __init__(self, width, height, table_height):
        # Constants
        self.WIDTH = width
        self.HEIGHT = height
        self.TABLE_HEIGHT = table_height
        self.PORTAL_HEIGHT = self.HEIGHT - self.TABLE_HEIGHT
        self.PORTAL_Y = self.TABLE_HEIGHT
        self.SCOREBOARD_HEIGHT = 60
        self.BACK_BUTTON_WIDTH = 100
        self.BACK_BUTTON_HEIGHT = 40
        self.SPIN_CIRCLE_RADIUS = 50
        self.MESSAGE_AREA_HEIGHT = 80
        self.MAX_MESSAGES = 3

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (128, 128, 128)
        self.DARK_GRAY = (64, 64, 64)
        self.RED = (255, 0, 0)

        # Initialize variables
        self.messages = []
        self.current_spin = (0, 0)
        self.spin_circle_center = (self.WIDTH - 100, self.PORTAL_Y + self.SCOREBOARD_HEIGHT + 70)
        self.back_button_rect = None
        self.font = pygame.font.Font(None, 36)

    def add_message(self, message):
        self.messages.append(message)
        if len(self.messages) > self.MAX_MESSAGES:
            self.messages.pop(0)

    def draw_player_arrow(self, screen, current_player):
        arrow_points = []
        base_x = 40 if current_player == 1 else self.WIDTH - 40
        base_y = self.PORTAL_Y + self.SCOREBOARD_HEIGHT // 2
        arrow_size = 20

        if current_player == 1:
            arrow_points = [
                (base_x + arrow_size, base_y - arrow_size//2),
                (base_x + arrow_size, base_y + arrow_size//2),
                (base_x, base_y)
            ]
        else:
            arrow_points = [
                (base_x - arrow_size, base_y - arrow_size//2),
                (base_x - arrow_size, base_y + arrow_size//2),
                (base_x, base_y)
            ]

        pygame.draw.polygon(screen, self.WHITE, arrow_points)

    def draw_messages(self, screen):
        # Draw messages in center area
        message_x = self.WIDTH // 2
        message_y = self.PORTAL_Y + self.SCOREBOARD_HEIGHT + 30
        for message in self.messages:
            text = self.font.render(message, True, self.WHITE)
            screen.blit(text, (message_x - text.get_width()//2, message_y))
            message_y += 25

    def handle_spin_input(self, mouse_pos):
        dx = mouse_pos[0] - self.spin_circle_center[0]
        dy = mouse_pos[1] - self.spin_circle_center[1]
        distance = math.sqrt(dx**2 + dy**2)

        if distance > self.SPIN_CIRCLE_RADIUS:
            dx = (dx / distance) * self.SPIN_CIRCLE_RADIUS
            dy = (dy / distance) * self.SPIN_CIRCLE_RADIUS

        side_spin = dx / self.SPIN_CIRCLE_RADIUS
        top_spin = -dy / self.SPIN_CIRCLE_RADIUS
        self.current_spin = (top_spin, side_spin)

    def draw_spin_indicator(self, screen):
        pygame.draw.circle(screen, self.WHITE, self.spin_circle_center, self.SPIN_CIRCLE_RADIUS, 2)
        indicator_x = self.spin_circle_center[0] + self.current_spin[1] * self.SPIN_CIRCLE_RADIUS
        indicator_y = self.spin_circle_center[1] - self.current_spin[0] * self.SPIN_CIRCLE_RADIUS
        pygame.draw.circle(screen, self.RED, (int(indicator_x), int(indicator_y)), 5)

    def draw(self, screen, player1_score, player2_score, current_player):
        # Draw portal background
        portal_rect = pygame.Rect(0, self.PORTAL_Y, self.WIDTH, self.PORTAL_HEIGHT)
        pygame.draw.rect(screen, self.DARK_GRAY, portal_rect)

        # Draw scoreboard
        scoreboard_rect = pygame.Rect(0, self.PORTAL_Y, self.WIDTH, self.SCOREBOARD_HEIGHT)
        pygame.draw.rect(screen, self.GRAY, scoreboard_rect)

        # Draw scores and player labels
        score_y = self.PORTAL_Y + self.SCOREBOARD_HEIGHT//2 - 15

        # Player 1 info (left side)
        player1_text = self.font.render("Player 1", True, self.WHITE)
        score_text = self.font.render(str(player1_score), True, self.WHITE)
        screen.blit(player1_text, (20, score_y))
        screen.blit(score_text, (80, score_y + 25))

        # Frame text (center)
        frame_text = self.font.render("Frame 1", True, self.WHITE)
        screen.blit(frame_text, (self.WIDTH//2 - frame_text.get_width()//2, score_y))

        # Player 2 info (right side)
        player2_text = self.font.render("Player 2", True, self.WHITE)
        score_text = self.font.render(str(player2_score), True, self.WHITE)
        screen.blit(player2_text, (self.WIDTH - 120, score_y))
        screen.blit(score_text, (self.WIDTH - 60, score_y + 25))

        # Draw player arrow
        self.draw_player_arrow(screen, current_player)

        # Draw back button
        self.back_button_rect = pygame.Rect(20, self.PORTAL_Y + self.SCOREBOARD_HEIGHT + 20, 
                                          self.BACK_BUTTON_WIDTH, self.BACK_BUTTON_HEIGHT)
        pygame.draw.rect(screen, self.WHITE, self.back_button_rect)
        back_text = self.font.render("Back", True, self.BLACK)
        screen.blit(back_text, (self.back_button_rect.centerx - back_text.get_width()//2,
                               self.back_button_rect.centery - back_text.get_height()//2))

        # Draw spin indicator
        self.draw_spin_indicator(screen)
        self.draw_messages(screen)
        

    def handle_click(self, pos):
        if self.back_button_rect and self.back_button_rect.collidepoint(pos):
            return "menu"
        return None
