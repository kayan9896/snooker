import pygame
import random
import math
from ball2 import Ball
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
      return all(ball.speed_x == 0 and ball.speed_y == 0 for ball in balls if ball.in_game)
    

    def check_foul(self, cue_ball, numbered_balls):
        self.foul = False
    
        if not self.cue_ball.in_game:
            self.foul = True
            self.add_message("Foul: Cue ball pocketed")
            return
    
        if not self.cue_ball.collision_order:
            self.foul = True
            self.add_message("Foul: No ball hit")
            return
    
        first_hit = self.cue_ball.collision_order[0]
        if first_hit.number != self.current_target_ball:
            self.foul = True
            self.add_message(f"Foul: Ball {self.current_target_ball} not hit first")
    
    def handle_game_logic(self, cue_ball, numbered_balls):
        self.check_foul(cue_ball, numbered_balls)
    
        current_ball_count = sum(ball.in_game for ball in self.numbered_balls)
        any_ball_pocketed = current_ball_count < self.ball_left
        self.ball_left = current_ball_count
    
        self.cue_ball.collision_order.clear()
        for ball in self.numbered_balls:
            ball.collision_order.clear()
    
        if self.foul:
            self.current_player = 3 - self.current_player
            self.resetting_cue_ball = True
            if not self.numbered_balls[8].in_game:
                self.numbered_balls[8].spot([self.cue_ball] + [b for b in self.numbered_balls if b.in_game])
        elif not self.numbered_balls[8].in_game:
            self.game_over = True
            self.add_message(f"Game Over! Player {self.current_player} wins!")
            self.reset_game(self.cue_ball, self.numbered_balls)
        else:
            if not any_ball_pocketed:
                self.current_player = 3 - self.current_player
                self.add_message(f"No balls pocketed. Player {self.current_player}'s turn")
    
        if not self.numbered_balls[self.current_target_ball - 1].in_game:
            for i in range(self.current_target_ball, 10):
                if i == 9 or self.numbered_balls[i - 1].in_game:
                    self.current_target_ball = i
                    self.add_message(f"New target ball: {self.current_target_ball}")
                    break
    
        if not self.cue_ball.in_game:
            self.cue_ball.reset()

    def reset_game(self, cue_ball, numbered_balls):
      self.game_over = False
      self.foul = False
      self.resetting_cue_ball = True
      self.current_player = 1
      self.current_target_ball = 1
      self.ball_left = 9  # Reset ball count
      self.is_initial_placement = True
    
      self.cue_ball.reset()
      for ball in self.numbered_balls:
          ball.reset()
    
      self.setup_rack()
    
    def is_valid_cue_position(self, x, y, cue_ball, other_balls, is_initial=False):
      # Basic boundary checks
      if (y < self.EDGE_WIDTH + self.buffer_HEIGHT + self.cue_ball.radius or 
          y > self.TABLE_HEIGHT - self.EDGE_WIDTH - self.buffer_HEIGHT - self.cue_ball.radius):
          return False
    
      # For initial placement or breaking shot:
      # Only allow placement in the "kitchen" (behind head string)
      if is_initial:
          head_string_x = self.EDGE_WIDTH + (self.WIDTH-self.EDGE_WIDTH*2-self.POCKET_RADIUS*2)/8 * 2
          if x > head_string_x or x < self.EDGE_WIDTH + self.buffer_HEIGHT + self.cue_ball.radius:
              return False
      else:
          # Regular reset: allow placement anywhere on the table
          if (x < self.EDGE_WIDTH + self.buffer_HEIGHT + self.cue_ball.radius or 
              x > self.WIDTH - self.EDGE_WIDTH - self.buffer_HEIGHT - self.cue_ball.radius):
              return False
    
      # Check collision with other balls
      for ball in other_balls:
          if ball.in_game:
              distance = math.sqrt((x - ball.x)**2 + (y - ball.y)**2)
              if distance < self.cue_ball.radius + ball.radius:
                  return False
    
      return True
    
    
    def run(self):
        # Main game loop
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
        
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    result = self.handle_portal_click(mouse_pos)
                    if result == "menu":
                        return "menu"  # Return to menu

                    # Check if click is in spin circle area
                    dx = mouse_pos[0] - self.spin_circle_center[0]
                    dy = mouse_pos[1] - self.spin_circle_center[1]
                    if math.sqrt(dx**2 + dy**2) <= self.SPIN_CIRCLE_RADIUS:
                        self.handle_spin_input(mouse_pos)
                        continue
                        
                    mouse_x, mouse_y = pygame.mouse.get_pos()
        
                    if self.resetting_cue_ball:
                        # Ball placement logic
                        if self.is_valid_cue_position(mouse_x, mouse_y, self.cue_ball, self.numbered_balls, self.is_initial_placement):
                            self.cue_ball.x, self.cue_ball.y = mouse_x, mouse_y
                            self.ball_placement_confirmed = True
                            print("Ball placement confirmed")
                            if self.is_initial_placement: self.is_initial_placement = False
        
                    elif self.cue_ball.speed_x == 0 and self.cue_ball.speed_y == 0 and not self.resetting_cue_ball:
                        # Shot preparation
                        if self.cue_ball.in_game:
                            self.mouse_pressed = True
                            self.stick.start_charging()

                elif event.type == pygame.MOUSEMOTION:
                    if pygame.mouse.get_pressed()[0]:  # Left button pressed
                        mouse_pos = event.pos
                        dx = mouse_pos[0] - self.spin_circle_center[0]
                        dy = mouse_pos[1] - self.spin_circle_center[1]
                        if math.sqrt(dx**2 + dy**2) <= self.SPIN_CIRCLE_RADIUS:
                            self.handle_spin_input(mouse_pos)
                        
                elif event.type == pygame.MOUSEBUTTONUP:
                    if self.resetting_cue_ball and self.ball_placement_confirmed:
                        # Confirm ball placement
                        self.resetting_cue_ball = False
                        self.ball_placement_confirmed = False
                        self.foul = False
                        self.shot_taken = False
                        print("Ready to shoot")
        
                    elif self.mouse_pressed and self.cue_ball.speed_x == 0 and self.cue_ball.speed_y == 0 and not self.resetting_cue_ball:
                        # Shot release
                        self.mouse_pressed = False
                        self.shot_ready = True
        
            # Get current mouse position
            mouse_pos = pygame.mouse.get_pos()
        
            # Update self.stick power if mouse is pressed
            if self.mouse_pressed and self.cue_ball.speed_x == 0 and self.cue_ball.speed_y == 0:
                # Calculate angle between ball and mouse for drawing and potential shot
                mouse_x, mouse_y = mouse_pos
                angle = math.atan2(mouse_y - self.cue_ball.y, mouse_x - self.cue_ball.x)
        
                # Update power
                self.stick.update_power()
        
                # Automatic shot release when max power is reached
                if self.stick.max_power_reached:
                    self.shot_ready = True
                    self.mouse_pressed=False
        
            # Check if shot is ready to be released
            if self.shot_ready and self.cue_ball.speed_x == 0 and self.cue_ball.speed_y == 0 and not self.shot_taken:
                # Get current mouse position for shot direction
                mouse_x, mouse_y = mouse_pos
        
                # Calculate velocity based on opposite direction of self.stick
                angle = math.atan2(mouse_y - self.cue_ball.y, mouse_x - self.cue_ball.x)
        
                # Use the calculated power
                self.cue_ball.speed_x = self.stick.power * math.cos(angle)
                self.cue_ball.speed_y = self.stick.power * math.sin(angle)

                self.cue_ball.top_spin = self.current_spin[0]*self.stick.power/25
                self.cue_ball.side_spin = self.current_spin[1]*self.stick.power/25
                
                # Hide self.stick after shot
                self.stick.visible = False
                # Reset charge
                self.stick.reset_charge()
                # Reset shot ready flag
                self.shot_ready = False
                # Mark shot as taken
                self.shot_taken = True
        
        
            # Update all balls
            self.cue_ball.move(self.numbered_balls)
            for ball in self.numbered_balls:
                ball.move([self.cue_ball] + [b for b in self.numbered_balls if b != ball])
        
            # Modify the drawing section:
            self.draw_pool_table()
            for ball in self.numbered_balls:
                ball.draw(self.screen)
            self.cue_ball.draw(self.screen)
            self.draw_portal()
        
        
            # Modify the game logic handling:
            if self.are_all_balls_stopped([self.cue_ball] + self.numbered_balls) and self.shot_taken:
                self.handle_game_logic(self.cue_ball, self.numbered_balls)
                self.shot_taken = False
        
            # Ball placement visualization during reset
            if self.resetting_cue_ball:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if self.is_valid_cue_position(mouse_x, mouse_y, self.cue_ball, self.numbered_balls,self.is_initial_placement):
                    temp_surface = pygame.Surface((self.cue_ball.radius*2, self.cue_ball.radius*2), pygame.SRCALPHA)
                    pygame.draw.circle(temp_surface, (200, 200, 200, 128), (self.cue_ball.radius, self.cue_ball.radius), self.cue_ball.radius)
                    self.screen.blit(temp_surface, (mouse_x - self.cue_ball.radius, mouse_y - self.cue_ball.radius))
        
            # Draw self.stick when ball is stationary
            if self.cue_ball.speed_x == 0 and self.cue_ball.speed_y == 0 and not self.resetting_cue_ball:
                if self.are_all_balls_stopped([self.cue_ball]+self.numbered_balls) and self.cue_ball.in_game:
                    self.stick.visible = True
                    mouse_x, mouse_y = mouse_pos
                    angle = math.atan2(mouse_y - self.cue_ball.y, mouse_x - self.cue_ball.x)
                    self.stick.draw(self.screen, self.cue_ball, mouse_pos, angle)
        
            # Display current player and self.foul status
            font = pygame.font.Font(None, 36)
            player_text = font.render(f"Player {self.current_player}", True, (255, 255, 255))
            self.screen.blit(player_text, (10, 10))
            if self.foul:
                self.foul_text = font.render("self.foul", True, (255, 0, 0))
                self.screen.blit(self.foul_text, (self.WIDTH - 100, 10))
        
            pygame.display.flip()
            pygame.time.Clock().tick(60)
        
        pygame.quit()
        
