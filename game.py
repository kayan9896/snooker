import pygame
import random
import math
from ball import Ball
from stick import Stick

class Game:
  def __init__(self):
      # Constants
      self.WIDTH, self.HEIGHT = 800, 400
      self.EDGE_WIDTH = 20
      self.POCKET_RADIUS = 15
      self.DIAMOND_SIZE = 5
      self.BALL_RADIUS = 8
      self.FRICTION_COEFFICIENT = 0.99
      self.offset = self.POCKET_RADIUS / math.sqrt(2)
      self.buffer_HEIGHT = self.POCKET_RADIUS

      # Colors
      self.WHITE = (255, 255, 255)
      self.BROWN = (102, 51, 0)
      self.BLUE = (0, 0, 255)
      self.BLACK = (0, 0, 0)

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

      # Initialize pygame and create self.screen
      pygame.init()
      self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))

      # Create game objects
      self.create_balls()
      self.stick = Stick()
      self.setup_rack()

  # Function to draw the pool table
  def draw_pool_table(self):
      # Draw the self.BLUE surface
      self.screen.fill(self.BLUE)

      # Draw the edges
      pygame.draw.rect(self.screen, self.BROWN, (0, 0, self.WIDTH, self.EDGE_WIDTH))
      pygame.draw.rect(self.screen, self.BROWN, (0, self.HEIGHT-self.EDGE_WIDTH, self.WIDTH, self.EDGE_WIDTH))
      pygame.draw.rect(self.screen, self.BROWN, (0, 0, self.EDGE_WIDTH, self.HEIGHT))
      pygame.draw.rect(self.screen, self.BROWN, (self.WIDTH-self.EDGE_WIDTH, 0, self.EDGE_WIDTH, self.HEIGHT))

      # Buffer color (slightly lighter self.BLUE to represent a raised surface)
      BUFFER_COLOR = (0, 0, 220)  # Slightly darker self.BLUE for the buffer border
      BUFFER_INNER_COLOR = self.BLUE   # Same as table surface

      # Calculate self.offset based on radius
      self.POCKET_RADIUS = self.POCKET_RADIUS
      self.offset = self.POCKET_RADIUS / math.sqrt(2)

      # Buffer self.HEIGHT (same as pocket radius)
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
      draw_buffer(self.EDGE_WIDTH + 2*self.offset, self.HEIGHT - self.EDGE_WIDTH, 
                  (self.WIDTH/2 - self.EDGE_WIDTH - 2*self.offset - self.POCKET_RADIUS))
      draw_buffer(self.WIDTH/2 + self.POCKET_RADIUS, self.HEIGHT - self.EDGE_WIDTH, 
                  (self.WIDTH/2 - self.EDGE_WIDTH - 2*self.offset - self.POCKET_RADIUS))

      # Draw buffers for left edge
      draw_buffer(self.EDGE_WIDTH, self.EDGE_WIDTH + 2*self.offset, 
                  (self.HEIGHT - 2*self.EDGE_WIDTH - 4*self.offset), is_vertical=True, is_top=True)

      # Draw buffers for right edge
      draw_buffer(self.WIDTH - self.EDGE_WIDTH, self.EDGE_WIDTH + 2*self.offset, 
                  (self.HEIGHT - 2*self.EDGE_WIDTH - 4*self.offset), is_vertical=True)


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
                        (self.EDGE_WIDTH + self.offset, self.HEIGHT - self.EDGE_WIDTH - self.offset), 
                        self.POCKET_RADIUS)

      # Bottom-right corner pocket
      pygame.draw.circle(self.screen, self.BLACK, 
                        (self.WIDTH - self.EDGE_WIDTH - self.offset, self.HEIGHT - self.EDGE_WIDTH - self.offset), 
                        self.POCKET_RADIUS)

      # Top middle pocket
      pygame.draw.circle(self.screen, self.BLACK, (self.WIDTH // 2, self.EDGE_WIDTH), self.POCKET_RADIUS)

      # Bottom middle pocket
      pygame.draw.circle(self.screen, self.BLACK, (self.WIDTH // 2, self.HEIGHT - self.EDGE_WIDTH), self.POCKET_RADIUS)


      # Draw the diamond spots
      for i in range(3):
          draw_diamond(self.EDGE_WIDTH/2 + (self.WIDTH/2 - self.EDGE_WIDTH*2)/4 * (i+1), self.EDGE_WIDTH/2, self.DIAMOND_SIZE, self.WHITE)
          draw_diamond(self.WIDTH - self.EDGE_WIDTH/2 - (self.WIDTH/2 - self.EDGE_WIDTH*2)/4 * (i+1), self.EDGE_WIDTH/2, self.DIAMOND_SIZE, self.WHITE)

          draw_diamond(self.EDGE_WIDTH/2 + (self.WIDTH/2 - self.EDGE_WIDTH*2)/4 * (i+1), self.HEIGHT - self.EDGE_WIDTH/2, self.DIAMOND_SIZE, self.WHITE)
          draw_diamond(self.WIDTH - self.EDGE_WIDTH/2 - (self.WIDTH/2 - self.EDGE_WIDTH*2)/4 * (i+1), self.HEIGHT - self.EDGE_WIDTH/2, self.DIAMOND_SIZE, self.WHITE)
          draw_diamond(self.EDGE_WIDTH/2, self.EDGE_WIDTH/2 + (self.HEIGHT-self.EDGE_WIDTH*2)/4 * (i+1), self.DIAMOND_SIZE, self.WHITE)
          draw_diamond(self.WIDTH-self.EDGE_WIDTH/2, self.EDGE_WIDTH/2 + (self.HEIGHT-self.EDGE_WIDTH*2)/4 * (i+1), self.DIAMOND_SIZE, self.WHITE)


      # Draw the head string
      head_string_x = int(self.EDGE_WIDTH + (self.WIDTH-self.EDGE_WIDTH*2-self.POCKET_RADIUS*2)/8 * 2)
      pygame.draw.line(self.screen, self.WHITE, 
                      (head_string_x, self.EDGE_WIDTH + self.buffer_HEIGHT), 
                      (head_string_x, self.HEIGHT - self.EDGE_WIDTH - self.buffer_HEIGHT), 2)

      # Draw the foot spot
      pygame.draw.circle(self.screen, self.WHITE, (int(self.WIDTH - self.EDGE_WIDTH - (self.WIDTH-self.EDGE_WIDTH*2-self.POCKET_RADIUS*2)/8 * 2), int(self.HEIGHT/2)), self.DIAMOND_SIZE)


  def create_balls(self):
    # Create cue ball
    self.cue_ball = Ball(
        self.EDGE_WIDTH + (self.WIDTH-self.EDGE_WIDTH*2-self.POCKET_RADIUS*2)/8 * 2,
        self.EDGE_WIDTH + self.buffer_HEIGHT + self.BALL_RADIUS,
        self.BALL_RADIUS, self.WHITE, self.WIDTH, self.HEIGHT,
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
        self.WIDTH, self.HEIGHT, self.EDGE_WIDTH,
        self.POCKET_RADIUS, self.offset,
        acceleration=0.05, number=number
    )


  def setup_rack(self):
      # Position for the apex ball (9 ball)
      apex_x = self.WIDTH - self.EDGE_WIDTH - (self.WIDTH-self.EDGE_WIDTH*2-self.POCKET_RADIUS*2)/8 * 2
      apex_y = self.HEIGHT/2
      ball_spacing = self.BALL_RADIUS * 2  # Slightly larger spacing to prevent overlapping

      # Calculate the total self.HEIGHT needed for 5 balls
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
      self.numbered_balls[0].y = apex_y  # Same self.HEIGHT as 9 ball

      # Place remaining ball at the back right
      remaining_ball = available_balls[6]
      remaining_ball.x = apex_x + row_offset * 2
      remaining_ball.y = apex_y  # Same self.HEIGHT as 9 ball

  # Modify the main game loop to handle all balls
  def are_all_balls_stopped(self,balls):
      return all(ball.speed_x == 0 and ball.speed_y == 0 for ball in balls if ball.in_game)


  def check_foul(self, cue_ball, numbered_balls):
      self.foul = False

      if not self.cue_ball.in_game:
          self.foul = True
          print("self.foul: Cue ball pocketed")
          return

      if not self.cue_ball.collision_order:
          self.foul = True
          print("self.foul: No ball hit")
          return

      # Check if the first ball hit was the current target ball
      first_hit = self.cue_ball.collision_order[0]
      if first_hit.number != self.current_target_ball:
          self.foul = True
          print(f"self.foul: Ball {self.current_target_ball} not hit first")


  def handle_game_logic(self, cue_ball, numbered_balls):

      self.check_foul(cue_ball, numbered_balls)

      # Check if any ball was pocketed by comparing current ball count with previous
      current_ball_count = sum(ball.in_game for ball in self.numbered_balls)
      any_ball_pocketed = current_ball_count < self.ball_left
      self.ball_left = current_ball_count

      # Clear collision orders
      self.cue_ball.collision_order.clear()
      for ball in self.numbered_balls:
          ball.collision_order.clear()

      if self.foul:
          self.current_player = 3 - self.current_player
          self.resetting_cue_ball = True
          # Spot the 9-ball if it was pocketed on a self.foul
          if not self.numbered_balls[8].in_game:
              self.numbered_balls[8].spot([self.cue_ball] + [b for b in self.numbered_balls if b.in_game])
      elif not self.numbered_balls[8].in_game:  # 9 ball legally pocketed
          self.game_over = True
          print("Game Over! Player", self.current_player, "wins!")
          self.reset_game(cue_ball, numbered_balls)
      else:
          # Switch player if no balls were pocketed on this shot
          if not any_ball_pocketed:
              self.current_player = 3 - self.current_player
              print(f"No balls pocketed. Switching to Player {self.current_player}")

      # Update self.current_target_ball if the current target was pocketed
      if not self.numbered_balls[self.current_target_ball - 1].in_game:
          # Find next target ball
          for i in range(self.current_target_ball, 10):
              if i == 9 or self.numbered_balls[i - 1].in_game:
                  self.current_target_ball = i
                  print(f"New target ball: {self.current_target_ball}")
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
          y > self.HEIGHT - self.EDGE_WIDTH - self.buffer_HEIGHT - self.cue_ball.radius):
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
    
