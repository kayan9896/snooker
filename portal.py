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
        self.LIGHT_BLUE = (100, 150, 255)
        self.LIGHT_YELLOW = (255, 255, 150)

        # Add new constants for section widths
        self.SIDE_SECTION_WIDTH = 200  # Width for player sections
        self.MIDDLE_SECTION_WIDTH = self.WIDTH - (2 * self.SIDE_SECTION_WIDTH)
        self.ARROW_SIZE = 20

        self.BALL_STATUS_RADIUS = 15
        self.INNER_CIRCLE_RADIUS = 10  # Radius for white inner circle
        self.BALL_STATUS_SPACING = 40
        self.BALL_STATUS_Y = self.PORTAL_Y + self.SCOREBOARD_HEIGHT + 20
        self.MESSAGE_Y = self.BALL_STATUS_Y + self.BALL_STATUS_RADIUS * 2 + 20  # More space before messages
        self.ball_font = pygame.font.Font(None, 24)

        
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

    def draw_ball_status(self, screen, balls):
        total_width = self.BALL_STATUS_SPACING * 8
        start_x = (self.WIDTH - total_width) // 2

        for i in range(9):
            ball_x = start_x + i * self.BALL_STATUS_SPACING
            ball_y = self.BALL_STATUS_Y
            ball = next((b for b in balls if b.number == i + 1), None)

            if ball and ball.in_game:
                # Draw colored outer circle only for balls still in play
                pygame.draw.circle(screen, ball.color, (ball_x, ball_y), self.BALL_STATUS_RADIUS)
                # Draw white inner circle
                pygame.draw.circle(screen, self.WHITE, (ball_x, ball_y), self.INNER_CIRCLE_RADIUS)
                # Draw ball number in black
                number_text = self.ball_font.render(str(i + 1), True, self.BLACK)
                number_rect = number_text.get_rect(center=(ball_x, ball_y))
                screen.blit(number_text, number_rect)
            else:
                # For potted balls or missing balls, just draw a light outline to show the position
                pygame.draw.circle(screen, (100, 100, 100), (ball_x, ball_y), self.BALL_STATUS_RADIUS, 1)

    
    def draw_player_arrow(self, screen, current_player):
        # Recalculate arrow position to be at the border between sections
        arrow_points = []
        if current_player == 1:
            # Right edge of left yellow section
            base_x = self.SIDE_SECTION_WIDTH
            arrow_points = [
                (base_x, self.PORTAL_Y + self.SCOREBOARD_HEIGHT/2 - self.ARROW_SIZE/2),
                (base_x, self.PORTAL_Y + self.SCOREBOARD_HEIGHT/2 + self.ARROW_SIZE/2),
                (base_x - self.ARROW_SIZE, self.PORTAL_Y + self.SCOREBOARD_HEIGHT/2)
            ]
        else:
            # Left edge of right yellow section
            base_x = self.WIDTH - self.SIDE_SECTION_WIDTH
            arrow_points = [
                (base_x, self.PORTAL_Y + self.SCOREBOARD_HEIGHT/2 - self.ARROW_SIZE/2),
                (base_x, self.PORTAL_Y + self.SCOREBOARD_HEIGHT/2 + self.ARROW_SIZE/2),
                (base_x + self.ARROW_SIZE, self.PORTAL_Y + self.SCOREBOARD_HEIGHT/2)
            ]
        pygame.draw.polygon(screen, self.BLACK, arrow_points)  # Changed color to BLACK

    
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

    def draw(self, screen, player1_score, player2_score, current_player, balls):
        # Draw portal background
        portal_rect = pygame.Rect(0, self.PORTAL_Y, self.WIDTH, self.PORTAL_HEIGHT)
        pygame.draw.rect(screen, self.DARK_GRAY, portal_rect)

        # Draw scoreboard sections
        # Left section (Player 1)
        left_section = pygame.Rect(0, self.PORTAL_Y, self.SIDE_SECTION_WIDTH, self.SCOREBOARD_HEIGHT)
        pygame.draw.rect(screen, self.LIGHT_YELLOW, left_section)

        # Middle section (Score)
        middle_section = pygame.Rect(self.SIDE_SECTION_WIDTH, self.PORTAL_Y, 
                                   self.MIDDLE_SECTION_WIDTH, self.SCOREBOARD_HEIGHT)
        pygame.draw.rect(screen, self.LIGHT_BLUE, middle_section)

        # Right section (Player 2)
        right_section = pygame.Rect(self.WIDTH - self.SIDE_SECTION_WIDTH, self.PORTAL_Y, 
                                  self.SIDE_SECTION_WIDTH, self.SCOREBOARD_HEIGHT)
        pygame.draw.rect(screen, self.LIGHT_YELLOW, right_section)

        # Center all text vertically in scoreboard
        text_y = self.PORTAL_Y + (self.SCOREBOARD_HEIGHT - self.font.get_height())//2

        # Draw Player 1 text (centered in left section)
        player1_text = self.font.render("Player 1", True, self.BLACK)
        player1_x = (self.SIDE_SECTION_WIDTH - player1_text.get_width())//2
        screen.blit(player1_text, (player1_x, text_y))

        # Draw scores and frame number in middle section
        score_text = f"{player1_score} (Frame 1) {player2_score}"
        score_surface = self.font.render(score_text, True, self.WHITE)
        score_x = self.SIDE_SECTION_WIDTH + (self.MIDDLE_SECTION_WIDTH - score_surface.get_width())//2
        screen.blit(score_surface, (score_x, text_y))

        # Draw Player 2 text (centered in right section)
        player2_text = self.font.render("Player 2", True, self.BLACK)
        player2_x = self.WIDTH - self.SIDE_SECTION_WIDTH + (self.SIDE_SECTION_WIDTH - player2_text.get_width())//2
        screen.blit(player2_text, (player2_x, text_y))

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

        # Draw messages in center area
        message_x = self.WIDTH // 2
        message_y = self.BALL_STATUS_Y + self.BALL_STATUS_RADIUS * 2 + 10  # Position below ball status
        for message in self.messages:
            text = self.font.render(message, True, self.WHITE)
            screen.blit(text, (message_x - text.get_width()//2, message_y))
            message_y += 25

        self.draw_ball_status(screen, balls)

    def handle_click(self, pos):
        if self.back_button_rect and self.back_button_rect.collidepoint(pos):
            return "menu"
        return None
