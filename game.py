import pygame
import random
import math
from ball import Ball
from stick import Stick

class Game:
    def __init__(self):
        # Constants
        self.WIDTH, self.TABLE_HEIGHT = 800, 400
        self.HEIGHT = 600
        self.EDGE_WIDTH = 20
        self.POCKET_RADIUS = 15
        self.DIAMOND_SIZE = 5
        self.BALL_RADIUS = 8
        self.FRICTION_COEFFICIENT = 0.99
        self.offset = self.POCKET_RADIUS / math.sqrt(2)
        self.buffer_HEIGHT = self.POCKET_RADIUS

        # Portal dimensions
        self.PORTAL_HEIGHT = self.HEIGHT - self.TABLE_HEIGHT
        self.PORTAL_Y = self.TABLE_HEIGHT

        # UI Elements dimensions
        self.SCOREBOARD_HEIGHT = 60
        self.BACK_BUTTON_WIDTH = 100
        self.BACK_BUTTON_HEIGHT = 40
        self.SPIN_CIRCLE_RADIUS = 50
        self.MESSAGE_AREA_HEIGHT = 80  # Height for game messages
        self.messages = []  # List to store game messages
        self.MAX_MESSAGES = 3  # Maximum number of messages to display

        # Arrow properties
        self.ARROW_SIZE = 20
        self.ARROW_MARGIN = 10

        self.current_spin = (0, 0)  # (top_spin, side_spin)
        self.spin_circle_center = (self.WIDTH - 100, self.PORTAL_Y + self.SCOREBOARD_HEIGHT + 70)

        # Colors
        self.WHITE = (255, 255, 255)
        self.BROWN = (102, 51, 0)
        self.BLUE = (0, 0, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (128, 128, 128)
        self.DARK_GRAY = (64, 64, 64)
        self.RED= (255, 0, 0)

        # Ball colors
        self.BALL_COLORS = {
          1: (255, 255, 0),        # Yellow
          2: (0, 0, 155),          # self.BLUE
          3: (255, 0, 0),          # Dark Red
          4: (128, 0, 128),        # Purple
          5: (255, 140, 0),        # Orange
          6: (0, 100, 0),          # Dark Green
          7: (139, 69, 19),        # self.BROWN
          8: (0, 0, 0),            # self.BLACK
          9: (255, 255, 0)         # Yellow (with stripe)
        }

        # Game state variables
        self.running = True
        self.mouse_pressed = False
        self.shot_ready = False
        self.resetting_cue_ball = True
        self.ball_placement_confirmed = False
        self.shot_taken = False
        self.current_player = 1
        self.foul = False
        self.game_over = False
        self.is_initial_placement = True
        self.current_target_ball = 1
        self.ball_left = 9

        # Scores
        self.player1_score = 0
        self.player2_score = 0

        # Initialize pygame and create screen
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.font = pygame.font.Font(None, 36)

        # Create game objects
        self.create_balls()
        self.stick = Stick()
        self.setup_rack()


    def add_message(self, message):
        """Add a message to be displayed in the message area"""
        self.messages.append(message)
        if len(self.messages) > self.MAX_MESSAGES:
            self.messages.pop(0)

    def draw_player_arrow(self):
        """Draw an arrow indicating current player's turn"""
        arrow_points = []
        if self.current_player == 1:
            # Draw arrow on the left
            base_x = 40
        else:
            # Draw arrow on the right
            base_x = self.WIDTH - 40

        base_y = self.PORTAL_Y + self.SCOREBOARD_HEIGHT // 2

        if self.current_player == 1:
            # Left-pointing arrow
            arrow_points = [
                (base_x + self.ARROW_SIZE, base_y - self.ARROW_SIZE//2),
                (base_x + self.ARROW_SIZE, base_y + self.ARROW_SIZE//2),
                (base_x, base_y)
            ]
        else:
            # Right-pointing arrow
            arrow_points = [
                (base_x - self.ARROW_SIZE, base_y - self.ARROW_SIZE//2),
                (base_x - self.ARROW_SIZE, base_y + self.ARROW_SIZE//2),
                (base_x, base_y)
            ]

        pygame.draw.polygon(self.screen, self.WHITE, arrow_points)

    def draw_messages(self):
        """Draw game messages in the message area"""
        message_y = self.PORTAL_Y + self.SCOREBOARD_HEIGHT + 10
        for message in self.messages:
            text = self.font.render(message, True, self.WHITE)
            self.screen.blit(text, (20, message_y))
            message_y += 25  # Space between messages

    def handle_spin_input(self, mouse_pos):
        # Calculate spin values based on mouse position relative to spin circle center
        dx = mouse_pos[0] - self.spin_circle_center[0]
        dy = mouse_pos[1] - self.spin_circle_center[1]

        # Normalize values to -1 to 1 range
        distance = math.sqrt(dx**2 + dy**2)
        if distance > self.SPIN_CIRCLE_RADIUS:
            dx = (dx / distance) * self.SPIN_CIRCLE_RADIUS
            dy = (dy / distance) * self.SPIN_CIRCLE_RADIUS

        # Convert to spin values (-1 to 1 range)
        side_spin = dx / self.SPIN_CIRCLE_RADIUS
        top_spin = -dy / self.SPIN_CIRCLE_RADIUS  # Negative because y increases downward

        self.current_spin = (top_spin, side_spin)

    def draw_spin_indicator(self):
        # Draw the base spin circle
        pygame.draw.circle(self.screen, self.WHITE, self.spin_circle_center, 
                         self.SPIN_CIRCLE_RADIUS, 2)

        # Draw the current spin position
        indicator_x = self.spin_circle_center[0] + self.current_spin[1] * self.SPIN_CIRCLE_RADIUS
        indicator_y = self.spin_circle_center[1] - self.current_spin[0] * self.SPIN_CIRCLE_RADIUS
        pygame.draw.circle(self.screen, self.RED, (int(indicator_x), int(indicator_y)), 5)

    def draw_portal(self):
        # Draw portal background
        portal_rect = pygame.Rect(0, self.PORTAL_Y, self.WIDTH, self.PORTAL_HEIGHT)
        pygame.draw.rect(self.screen, self.DARK_GRAY, portal_rect)

        # Draw scoreboard
        scoreboard_rect = pygame.Rect(0, self.PORTAL_Y, self.WIDTH, self.SCOREBOARD_HEIGHT)
        pygame.draw.rect(self.screen, self.GRAY, scoreboard_rect)

        # Draw player labels and scores (centered vertically in scoreboard)
        score_y = self.PORTAL_Y + self.SCOREBOARD_HEIGHT//2 - 15

        # Player 1 score (left side)
        score_text = self.font.render(str(self.player1_score), True, self.WHITE)
        self.screen.blit(score_text, (80, score_y))

        # Frame text (center)
        frame_text = self.font.render("Frame 1", True, self.WHITE)
        self.screen.blit(frame_text, (self.WIDTH//2 - frame_text.get_width()//2, score_y))

        # Player 2 score (right side)
        score_text = self.font.render(str(self.player2_score), True, self.WHITE)
        self.screen.blit(score_text, (self.WIDTH - 80 - score_text.get_width(), score_y))

        # Draw the current player indicator arrow
        self.draw_player_arrow()

        # Draw back button
        self.back_button_rect = pygame.Rect(20, self.PORTAL_Y + self.SCOREBOARD_HEIGHT + 20, 
                                          self.BACK_BUTTON_WIDTH, self.BACK_BUTTON_HEIGHT)
        pygame.draw.rect(self.screen, self.WHITE, self.back_button_rect)
        back_text = self.font.render("Back", True, self.BLACK)
        self.screen.blit(back_text, (self.back_button_rect.centerx - back_text.get_width()//2,
                                   self.back_button_rect.centery - back_text.get_height()//2))

        # Draw spin circle

        self.draw_spin_indicator()

        # Draw messages
        self.draw_messages()


    def handle_portal_click(self, pos):
      # Check if back button was clicked
      if self.back_button_rect.collidepoint(pos):
          return "menu"
      return None


    # Function to draw the pool table
    def draw_pool_table(self):
      # Draw the self.BLUE surface
      self.screen.fill(self.BLUE)

      # Draw the edges
      pygame.draw.rect(self.screen, self.BROWN, (0, 0, self.WIDTH, self.EDGE_WIDTH))
      pygame.draw.rect(self.screen, self.BROWN, (0, self.TABLE_HEIGHT-self.EDGE_WIDTH, self.WIDTH, self.EDGE_WIDTH))
      pygame.draw.rect(self.screen, self.BROWN, (0, 0, self.EDGE_WIDTH, self.TABLE_HEIGHT))
      pygame.draw.rect(self.screen, self.BROWN, (self.WIDTH-self.EDGE_WIDTH, 0, self.EDGE_WIDTH, self.TABLE_HEIGHT))

      # Buffer color (slightly lighter self.BLUE to represent a raised surface)
      BUFFER_COLOR = (0, 0, 220)  # Slightly darker self.BLUE for the buffer border
      BUFFER_INNER_COLOR = self.BLUE   # Same as table surface

      # Calculate self.offset based on radius
      self.POCKET_RADIUS = self.POCKET_RADIUS
      self.offset = self.POCKET_RADIUS / math.sqrt(2)

      # Buffer self.TABLE_HEIGHT (same as pocket radius)
      self.buffer_HEIGHT = self.POCKET_RADIUS

      # Function to draw a diamond
      def draw_diamond(x, y, size, color):
          pygame.draw.polygon(self.screen, color, [(x, y-size), (x+size, y), (x, y+size), (x-size, y)])

      # Function to draw a buffer
      def draw_buffer(start_x, start_y, length, is_vertical=False, is_top=False):
          corner_radius = 3  # Radius for rounding the corners of the shorter base

          if is_vertical:
              if is_top:
                  # Main trapezoid
                  points = [
                      (start_x, start_y),  # Top left
                      (start_x + self.buffer_HEIGHT, start_y + self.offset),  # Top right
                      (start_x + self.buffer_HEIGHT, start_y + length - self.offset),  # Bottom right
                      (start_x, start_y + length)  # Bottom left
                  ]
                  # Round corners for the right side
                  pygame.draw.circle(self.screen, BUFFER_COLOR, 
                                   (int(start_x + self.buffer_HEIGHT), int(start_y + self.offset)), 
                                   corner_radius)
                  pygame.draw.circle(self.screen, BUFFER_COLOR, 
                                   (int(start_x + self.buffer_HEIGHT), int(start_y + length - self.offset)), 
                                   corner_radius)
              else:
                  points = [
                      (start_x - self.buffer_HEIGHT, start_y + self.offset),  # Top left
                      (start_x, start_y),  # Top right
                      (start_x, start_y + length),  # Bottom right
                      (start_x - self.buffer_HEIGHT, start_y + length - self.offset)  # Bottom left
                  ]
                  # Round corners for the left side
                  pygame.draw.circle(self.screen, BUFFER_COLOR, 
                                   (int(start_x - self.buffer_HEIGHT), int(start_y + self.offset)), 
                                   corner_radius)
                  pygame.draw.circle(self.screen, BUFFER_COLOR, 
                                   (int(start_x - self.buffer_HEIGHT), int(start_y + length - self.offset)), 
                                   corner_radius)
          else:
              if is_top:
                  points = [
                      (start_x, start_y),  # Top left
                      (start_x + self.offset, start_y + self.buffer_HEIGHT),  # Bottom left
                      (start_x + length - self.offset, start_y + self.buffer_HEIGHT),  # Bottom right
                      (start_x + length, start_y)  # Top right
                  ]
                  # Round corners for the bottom side
                  pygame.draw.circle(self.screen, BUFFER_COLOR, 
                                   (int(start_x + self.offset), int(start_y + self.buffer_HEIGHT)), 
                                   corner_radius)
                  pygame.draw.circle(self.screen, BUFFER_COLOR, 
                                   (int(start_x + length - self.offset), int(start_y + self.buffer_HEIGHT)), 
                                   corner_radius)
              else:
                  points = [
                      (start_x + self.offset, start_y - self.buffer_HEIGHT),  # Top left
                      (start_x, start_y),  # Bottom left
                      (start_x + length, start_y),  # Bottom right
                      (start_x + length - self.offset, start_y - self.buffer_HEIGHT)  # Top right
                  ]
                  # Round corners for the top side
                  pygame.draw.circle(self.screen, BUFFER_COLOR, 
                                   (int(start_x + self.offset), int(start_y - self.buffer_HEIGHT)), 
                                   corner_radius)
                  pygame.draw.circle(self.screen, BUFFER_COLOR, 
                                   (int(start_x + length - self.offset), int(start_y - self.buffer_HEIGHT)), 
                                   corner_radius)

          pygame.draw.polygon(self.screen, BUFFER_COLOR, points)

          # Draw the inner part (slightly smaller)
          if is_vertical:
              if is_top:
                  inner_points = [
                      (start_x + 1, start_y + 1),
                      (start_x + self.buffer_HEIGHT - 1, start_y + self.offset + 1),
                      (start_x + self.buffer_HEIGHT - 1, start_y + length - self.offset - 1),
                      (start_x + 1, start_y + length - 1)
                  ]
              else:
                  inner_points = [
                      (start_x - self.buffer_HEIGHT + 1, start_y + self.offset + 1),
                      (start_x - 1, start_y + 1),
                      (start_x - 1, start_y + length - 1),
                      (start_x - self.buffer_HEIGHT + 1, start_y + length - self.offset - 1)
                  ]
          else:
              if is_top:
                  inner_points = [
                      (start_x + 1, start_y + 1),
                      (start_x + self.offset + 1, start_y + self.buffer_HEIGHT - 1),
                      (start_x + length - self.offset - 1, start_y + self.buffer_HEIGHT - 1),
                      (start_x + length - 1, start_y + 1)
                  ]
              else:
                  inner_points = [
                      (start_x + self.offset + 1, start_y - self.buffer_HEIGHT + 1),
                      (start_x + 1, start_y - 1),
                      (start_x + length - 1, start_y - 1),
                      (start_x + length - self.offset - 1, start_y - self.buffer_HEIGHT + 1)
                  ]

          pygame.draw.polygon(self.screen, BUFFER_INNER_COLOR, inner_points)
      # Buffer calls:
      # Draw buffers for top edge
      draw_buffer(self.EDGE_WIDTH + 2*self.offset, self.EDGE_WIDTH, 
                  (self.WIDTH/2 - self.EDGE_WIDTH - 2*self.offset - self.POCKET_RADIUS), is_top=True)
      draw_buffer(self.WIDTH/2 + self.POCKET_RADIUS, self.EDGE_WIDTH, 
                  (self.WIDTH/2 - self.EDGE_WIDTH - 2*self.offset - self.POCKET_RADIUS), is_top=True)

      # Draw buffers for bottom edge
      draw_buffer(self.EDGE_WIDTH + 2*self.offset, self.TABLE_HEIGHT - self.EDGE_WIDTH, 
                  (self.WIDTH/2 - self.EDGE_WIDTH - 2*self.offset - self.POCKET_RADIUS))
      draw_buffer(self.WIDTH/2 + self.POCKET_RADIUS, self.TABLE_HEIGHT - self.EDGE_WIDTH, 
                  (self.WIDTH/2 - self.EDGE_WIDTH - 2*self.offset - self.POCKET_RADIUS))

      # Draw buffers for left edge
      draw_buffer(self.EDGE_WIDTH, self.EDGE_WIDTH + 2*self.offset, 
                  (self.TABLE_HEIGHT - 2*self.EDGE_WIDTH - 4*self.offset), is_vertical=True, is_top=True)

      # Draw buffers for right edge
      draw_buffer(self.WIDTH - self.EDGE_WIDTH, self.EDGE_WIDTH + 2*self.offset, 
                  (self.TABLE_HEIGHT - 2*self.EDGE_WIDTH - 4*self.offset), is_vertical=True)


      # Draw the pockets
      # For each corner pocket, start from inner edge intersection and self.offset the center

      # Top-left corner pocket
      pygame.draw.circle(self.screen, self.BLACK, 
                        (self.EDGE_WIDTH + self.offset, self.EDGE_WIDTH + self.offset), 
                        self.POCKET_RADIUS)

      # Top-right corner pocket
      pygame.draw.circle(self.screen, self.BLACK, 
                        (self.WIDTH - self.EDGE_WIDTH - self.offset, self.EDGE_WIDTH + self.offset), 
                        self.POCKET_RADIUS)

      # Bottom-left corner pocket
      pygame.draw.circle(self.screen, self.BLACK, 
                        (self.EDGE_WIDTH + self.offset, self.TABLE_HEIGHT - self.EDGE_WIDTH - self.offset), 
                        self.POCKET_RADIUS)

      # Bottom-right corner pocket
      pygame.draw.circle(self.screen, self.BLACK, 
                        (self.WIDTH - self.EDGE_WIDTH - self.offset, self.TABLE_HEIGHT - self.EDGE_WIDTH - self.offset), 
                        self.POCKET_RADIUS)

      # Top middle pocket
      pygame.draw.circle(self.screen, self.BLACK, (self.WIDTH // 2, self.EDGE_WIDTH), self.POCKET_RADIUS)

      # Bottom middle pocket
      pygame.draw.circle(self.screen, self.BLACK, (self.WIDTH // 2, self.TABLE_HEIGHT - self.EDGE_WIDTH), self.POCKET_RADIUS)


      # Draw the diamond spots
      for i in range(3):
          draw_diamond(self.EDGE_WIDTH/2 + (self.WIDTH/2 - self.EDGE_WIDTH*2)/4 * (i+1), self.EDGE_WIDTH/2, self.DIAMOND_SIZE, self.WHITE)
          draw_diamond(self.WIDTH - self.EDGE_WIDTH/2 - (self.WIDTH/2 - self.EDGE_WIDTH*2)/4 * (i+1), self.EDGE_WIDTH/2, self.DIAMOND_SIZE, self.WHITE)

          draw_diamond(self.EDGE_WIDTH/2 + (self.WIDTH/2 - self.EDGE_WIDTH*2)/4 * (i+1), self.TABLE_HEIGHT - self.EDGE_WIDTH/2, self.DIAMOND_SIZE, self.WHITE)
          draw_diamond(self.WIDTH - self.EDGE_WIDTH/2 - (self.WIDTH/2 - self.EDGE_WIDTH*2)/4 * (i+1), self.TABLE_HEIGHT - self.EDGE_WIDTH/2, self.DIAMOND_SIZE, self.WHITE)
          draw_diamond(self.EDGE_WIDTH/2, self.EDGE_WIDTH/2 + (self.TABLE_HEIGHT-self.EDGE_WIDTH*2)/4 * (i+1), self.DIAMOND_SIZE, self.WHITE)
          draw_diamond(self.WIDTH-self.EDGE_WIDTH/2, self.EDGE_WIDTH/2 + (self.TABLE_HEIGHT-self.EDGE_WIDTH*2)/4 * (i+1), self.DIAMOND_SIZE, self.WHITE)


      # Draw the head string
      head_string_x = int(self.EDGE_WIDTH + (self.WIDTH-self.EDGE_WIDTH*2-self.POCKET_RADIUS*2)/8 * 2)
      pygame.draw.line(self.screen, self.WHITE, 
                      (head_string_x, self.EDGE_WIDTH + self.buffer_HEIGHT), 
                      (head_string_x, self.TABLE_HEIGHT - self.EDGE_WIDTH - self.buffer_HEIGHT), 2)

      # Draw the foot spot
      pygame.draw.circle(self.screen, self.WHITE, (int(self.WIDTH - self.EDGE_WIDTH - (self.WIDTH-self.EDGE_WIDTH*2-self.POCKET_RADIUS*2)/8 * 2), int(self.TABLE_HEIGHT/2)), self.DIAMOND_SIZE)


    def create_balls(self):
        # Create cue ball
        self.cue_ball = Ball(
            self.EDGE_WIDTH + (self.WIDTH-self.EDGE_WIDTH*2-self.POCKET_RADIUS*2)/8 * 2,
            self.EDGE_WIDTH + self.buffer_HEIGHT + self.BALL_RADIUS,
            self.BALL_RADIUS, self.WHITE, self.WIDTH, self.TABLE_HEIGHT,
            self.EDGE_WIDTH, self.POCKET_RADIUS, self.offset,
            acceleration=0.05, number=0
        )

        # Create numbered balls
        self.numbered_balls = [
            self.create_numbered_ball(i, 0, 0) for i in range(1, 10)
        ]

    def create_numbered_ball(self, number, x, y):
        return Ball(
            x, y, self.BALL_RADIUS, self.BALL_COLORS[number],
            self.WIDTH, self.TABLE_HEIGHT, self.EDGE_WIDTH,
            self.POCKET_RADIUS, self.offset,
            acceleration=0.05, number=number
        )


    def setup_rack(self):
      # Position for the apex ball (9 ball)
      apex_x = self.WIDTH - self.EDGE_WIDTH - (self.WIDTH-self.EDGE_WIDTH*2-self.POCKET_RADIUS*2)/8 * 2
      apex_y = self.TABLE_HEIGHT/2
      ball_spacing = self.BALL_RADIUS * 2  # Slightly larger spacing to prevent overlapping

      # Calculate the total self.TABLE_HEIGHT needed for 5 balls
      total_HEIGHT = ball_spacing * 4  # Space for 5 balls vertically
      start_y = apex_y - total_HEIGHT/2  # Start from the top

      # Set the 9 ball position (center of the rack)
      self.numbered_balls[8].x = apex_x  # 9 ball (index 8)
      self.numbered_balls[8].y = apex_y  # Center position

      # Available balls for random placement (excluding 1 and 9)
      available_balls = self.numbered_balls[1:8]  # balls 2-8
      random.shuffle(available_balls)

      # Place two random balls in the same vertical line as 9 ball
      available_balls[0].x = apex_x
      available_balls[0].y = apex_y - ball_spacing  # One ball above 9
      available_balls[1].x = apex_x
      available_balls[1].y = apex_y + ball_spacing  # One ball below 9

      # Row self.offset for the diamond shape
      row_offset = ball_spacing * math.sin(math.pi/3)  # 60 degree angle

      # Place two balls on each side (maintaining diamond shape)
      available_balls[2].x = apex_x - row_offset
      available_balls[2].y = apex_y - ball_spacing/2

      available_balls[3].x = apex_x - row_offset
      available_balls[3].y = apex_y + ball_spacing/2

      available_balls[4].x = apex_x + row_offset
      available_balls[4].y = apex_y - ball_spacing/2

      available_balls[5].x = apex_x + row_offset
      available_balls[5].y = apex_y + ball_spacing/2

      # Place 1 ball at the back left
      self.numbered_balls[0].x = apex_x - row_offset * 2  # 1 ball
      self.numbered_balls[0].y = apex_y  # Same self.TABLE_HEIGHT as 9 ball

      # Place remaining ball at the back right
      remaining_ball = available_balls[6]
      remaining_ball.x = apex_x + row_offset * 2
      remaining_ball.y = apex_y  # Same self.TABLE_HEIGHT as 9 ball

    # Modify the main game loop to handle all balls
    def are_all_balls_stopped(self,balls):
      return all(ball.speed_x == 0 and ball.speed_y == 0 and ball.rotational_speed_x==0 and ball.rotational_speed_y==0 for ball in balls if ball.in_game)
