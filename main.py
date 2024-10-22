import pygame
import math
from ball import Ball
from stick import Stick
# Initialize Pygame
pygame.init()

WHITE = (255, 255, 255)
BROWN = (102, 51, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Set up some constants
WIDTH, HEIGHT = 800, 400
EDGE_WIDTH = 20
POCKET_RADIUS = 15
DIAMOND_SIZE = 5
BALL_RADIUS = 8
FRICTION_COEFFICIENT = 0.99
pocket_radius=POCKET_RADIUS
offset = pocket_radius / math.sqrt(2)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))

def draw_arc(x, y, radius, start_angle, end_angle, color):
    pygame.draw.arc(screen, color, (x, y, radius * 2, radius * 2), start_angle, end_angle, 3)

# Function to draw a diamond
def draw_diamond(x, y, size, color):
    pygame.draw.polygon(screen, color, [(x, y-size), (x+size, y), (x, y+size), (x-size, y)])


# Function to draw the pool table
def draw_pool_table():
    # Draw the blue surface
    screen.fill(BLUE)

    # Draw the edges
    pygame.draw.rect(screen, BROWN, (0, 0, WIDTH, EDGE_WIDTH))
    pygame.draw.rect(screen, BROWN, (0, HEIGHT-EDGE_WIDTH, WIDTH, EDGE_WIDTH))
    pygame.draw.rect(screen, BROWN, (0, 0, EDGE_WIDTH, HEIGHT))
    pygame.draw.rect(screen, BROWN, (WIDTH-EDGE_WIDTH, 0, EDGE_WIDTH, HEIGHT))

    # Buffer color (slightly lighter blue to represent a raised surface)
    BUFFER_COLOR = (0, 0, 220)  # Slightly darker blue for the buffer border
    BUFFER_INNER_COLOR = BLUE   # Same as table surface

    # Calculate offset based on radius
    pocket_radius = POCKET_RADIUS
    offset = pocket_radius / math.sqrt(2)

    # Buffer height (same as pocket radius)
    buffer_height = pocket_radius

    # Function to draw a buffer
    def draw_buffer(start_x, start_y, length, is_vertical=False, is_top=False):
        corner_radius = 3  # Radius for rounding the corners of the shorter base

        if is_vertical:
            if is_top:
                # Main trapezoid
                points = [
                    (start_x, start_y),  # Top left
                    (start_x + buffer_height, start_y + offset),  # Top right
                    (start_x + buffer_height, start_y + length - offset),  # Bottom right
                    (start_x, start_y + length)  # Bottom left
                ]
                # Round corners for the right side
                pygame.draw.circle(screen, BUFFER_COLOR, 
                                 (int(start_x + buffer_height), int(start_y + offset)), 
                                 corner_radius)
                pygame.draw.circle(screen, BUFFER_COLOR, 
                                 (int(start_x + buffer_height), int(start_y + length - offset)), 
                                 corner_radius)
            else:
                points = [
                    (start_x - buffer_height, start_y + offset),  # Top left
                    (start_x, start_y),  # Top right
                    (start_x, start_y + length),  # Bottom right
                    (start_x - buffer_height, start_y + length - offset)  # Bottom left
                ]
                # Round corners for the left side
                pygame.draw.circle(screen, BUFFER_COLOR, 
                                 (int(start_x - buffer_height), int(start_y + offset)), 
                                 corner_radius)
                pygame.draw.circle(screen, BUFFER_COLOR, 
                                 (int(start_x - buffer_height), int(start_y + length - offset)), 
                                 corner_radius)
        else:
            if is_top:
                points = [
                    (start_x, start_y),  # Top left
                    (start_x + offset, start_y + buffer_height),  # Bottom left
                    (start_x + length - offset, start_y + buffer_height),  # Bottom right
                    (start_x + length, start_y)  # Top right
                ]
                # Round corners for the bottom side
                pygame.draw.circle(screen, BUFFER_COLOR, 
                                 (int(start_x + offset), int(start_y + buffer_height)), 
                                 corner_radius)
                pygame.draw.circle(screen, BUFFER_COLOR, 
                                 (int(start_x + length - offset), int(start_y + buffer_height)), 
                                 corner_radius)
            else:
                points = [
                    (start_x + offset, start_y - buffer_height),  # Top left
                    (start_x, start_y),  # Bottom left
                    (start_x + length, start_y),  # Bottom right
                    (start_x + length - offset, start_y - buffer_height)  # Top right
                ]
                # Round corners for the top side
                pygame.draw.circle(screen, BUFFER_COLOR, 
                                 (int(start_x + offset), int(start_y - buffer_height)), 
                                 corner_radius)
                pygame.draw.circle(screen, BUFFER_COLOR, 
                                 (int(start_x + length - offset), int(start_y - buffer_height)), 
                                 corner_radius)

        pygame.draw.polygon(screen, BUFFER_COLOR, points)

        # Draw the inner part (slightly smaller)
        if is_vertical:
            if is_top:
                inner_points = [
                    (start_x + 1, start_y + 1),
                    (start_x + buffer_height - 1, start_y + offset + 1),
                    (start_x + buffer_height - 1, start_y + length - offset - 1),
                    (start_x + 1, start_y + length - 1)
                ]
            else:
                inner_points = [
                    (start_x - buffer_height + 1, start_y + offset + 1),
                    (start_x - 1, start_y + 1),
                    (start_x - 1, start_y + length - 1),
                    (start_x - buffer_height + 1, start_y + length - offset - 1)
                ]
        else:
            if is_top:
                inner_points = [
                    (start_x + 1, start_y + 1),
                    (start_x + offset + 1, start_y + buffer_height - 1),
                    (start_x + length - offset - 1, start_y + buffer_height - 1),
                    (start_x + length - 1, start_y + 1)
                ]
            else:
                inner_points = [
                    (start_x + offset + 1, start_y - buffer_height + 1),
                    (start_x + 1, start_y - 1),
                    (start_x + length - 1, start_y - 1),
                    (start_x + length - offset - 1, start_y - buffer_height + 1)
                ]

        pygame.draw.polygon(screen, BUFFER_INNER_COLOR, inner_points)
    # Buffer calls:
    # Draw buffers for top edge
    draw_buffer(EDGE_WIDTH + 2*offset, EDGE_WIDTH, 
                (WIDTH/2 - EDGE_WIDTH - 2*offset - pocket_radius), is_top=True)
    draw_buffer(WIDTH/2 + pocket_radius, EDGE_WIDTH, 
                (WIDTH/2 - EDGE_WIDTH - 2*offset - pocket_radius), is_top=True)

    # Draw buffers for bottom edge
    draw_buffer(EDGE_WIDTH + 2*offset, HEIGHT - EDGE_WIDTH, 
                (WIDTH/2 - EDGE_WIDTH - 2*offset - pocket_radius))
    draw_buffer(WIDTH/2 + pocket_radius, HEIGHT - EDGE_WIDTH, 
                (WIDTH/2 - EDGE_WIDTH - 2*offset - pocket_radius))

    # Draw buffers for left edge
    draw_buffer(EDGE_WIDTH, EDGE_WIDTH + 2*offset, 
                (HEIGHT - 2*EDGE_WIDTH - 4*offset), is_vertical=True, is_top=True)

    # Draw buffers for right edge
    draw_buffer(WIDTH - EDGE_WIDTH, EDGE_WIDTH + 2*offset, 
                (HEIGHT - 2*EDGE_WIDTH - 4*offset), is_vertical=True)


    # Draw the pockets
    # For each corner pocket, start from inner edge intersection and offset the center

    # Top-left corner pocket
    pygame.draw.circle(screen, BLACK, 
                      (EDGE_WIDTH + offset, EDGE_WIDTH + offset), 
                      pocket_radius)

    # Top-right corner pocket
    pygame.draw.circle(screen, BLACK, 
                      (WIDTH - EDGE_WIDTH - offset, EDGE_WIDTH + offset), 
                      pocket_radius)

    # Bottom-left corner pocket
    pygame.draw.circle(screen, BLACK, 
                      (EDGE_WIDTH + offset, HEIGHT - EDGE_WIDTH - offset), 
                      pocket_radius)

    # Bottom-right corner pocket
    pygame.draw.circle(screen, BLACK, 
                      (WIDTH - EDGE_WIDTH - offset, HEIGHT - EDGE_WIDTH - offset), 
                      pocket_radius)

    # Top middle pocket
    pygame.draw.circle(screen, BLACK, (WIDTH // 2, EDGE_WIDTH), pocket_radius)

    # Bottom middle pocket
    pygame.draw.circle(screen, BLACK, (WIDTH // 2, HEIGHT - EDGE_WIDTH), pocket_radius)


    # Draw the diamond spots
    for i in range(3):
        draw_diamond(EDGE_WIDTH/2 + (WIDTH/2 - EDGE_WIDTH*2)/4 * (i+1), EDGE_WIDTH/2, DIAMOND_SIZE, WHITE)
        draw_diamond(WIDTH - EDGE_WIDTH/2 - (WIDTH/2 - EDGE_WIDTH*2)/4 * (i+1), EDGE_WIDTH/2, DIAMOND_SIZE, WHITE)

        draw_diamond(EDGE_WIDTH/2 + (WIDTH/2 - EDGE_WIDTH*2)/4 * (i+1), HEIGHT - EDGE_WIDTH/2, DIAMOND_SIZE, WHITE)
        draw_diamond(WIDTH - EDGE_WIDTH/2 - (WIDTH/2 - EDGE_WIDTH*2)/4 * (i+1), HEIGHT - EDGE_WIDTH/2, DIAMOND_SIZE, WHITE)
        draw_diamond(EDGE_WIDTH/2, EDGE_WIDTH/2 + (HEIGHT-EDGE_WIDTH*2)/4 * (i+1), DIAMOND_SIZE, WHITE)
        draw_diamond(WIDTH-EDGE_WIDTH/2, EDGE_WIDTH/2 + (HEIGHT-EDGE_WIDTH*2)/4 * (i+1), DIAMOND_SIZE, WHITE)


    # Draw the head string
    head_string_x = int(EDGE_WIDTH + (WIDTH-EDGE_WIDTH*2-POCKET_RADIUS*2)/8 * 2)
    pygame.draw.line(screen, WHITE, 
                    (head_string_x, EDGE_WIDTH + buffer_height), 
                    (head_string_x, HEIGHT - EDGE_WIDTH - buffer_height), 2)

    # Draw the foot spot
    pygame.draw.circle(screen, WHITE, (int(WIDTH - EDGE_WIDTH - (WIDTH-EDGE_WIDTH*2-POCKET_RADIUS*2)/8 * 2), int(HEIGHT/2)), DIAMOND_SIZE)



buffer_height=POCKET_RADIUS
# Main loop
ball = Ball(EDGE_WIDTH + (WIDTH-EDGE_WIDTH*2-POCKET_RADIUS*2)/8 * 2, 
      EDGE_WIDTH + buffer_height + BALL_RADIUS, 
      BALL_RADIUS, WHITE, WIDTH, HEIGHT, EDGE_WIDTH, POCKET_RADIUS, offset, 
      acceleration=0.05, resetable=True)

yellow_ball = Ball(WIDTH - EDGE_WIDTH - (WIDTH-EDGE_WIDTH*2-POCKET_RADIUS*2)/8 * 2, 
       HEIGHT/2, 
       BALL_RADIUS, (255, 255, 0), WIDTH, HEIGHT, EDGE_WIDTH, POCKET_RADIUS, offset, 
       acceleration=0.05, resetable=False)

red_ball = Ball(WIDTH - EDGE_WIDTH - (WIDTH-EDGE_WIDTH*2-POCKET_RADIUS*2)/8 * 2 + BALL_RADIUS * 2, 
    HEIGHT/2, 
    BALL_RADIUS, (255, 0, 0), WIDTH, HEIGHT, EDGE_WIDTH, POCKET_RADIUS, offset, 
    acceleration=0.05, resetable=False)

stick = Stick()

# Main game loop modifications
running = True
mouse_pressed = False
shot_ready = False  # New flag to control shot release

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if ball.speed_x == 0 and ball.speed_y == 0:  # Only allow shot if ball is stationary
                mouse_pressed = True
                stick.start_charging()

        elif event.type == pygame.MOUSEBUTTONUP:
            if ball.speed_x == 0 and ball.speed_y == 0:
                mouse_pressed = False
                shot_ready = True

    # Get current mouse position
    mouse_pos = pygame.mouse.get_pos()

    # Update ball position
    ball.move([red_ball, yellow_ball])
    yellow_ball.move([ball, red_ball])
    red_ball.move([ball, yellow_ball])


    # Update stick power if mouse is pressed
    if mouse_pressed and ball.speed_x == 0 and ball.speed_y == 0:
        # Calculate angle between ball and mouse for drawing and potential shot
        mouse_x, mouse_y = mouse_pos
        angle = math.atan2(mouse_y - ball.y, mouse_x - ball.x)

        # Update power
        stick.update_power()

        # Automatic shot release when max power is reached
        if stick.max_power_reached:
            shot_ready = True

    # Check if shot is ready to be released
    if shot_ready and ball.speed_x == 0 and ball.speed_y == 0:
        # Get current mouse position for shot direction
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Calculate velocity based on opposite direction of stick
        angle = math.atan2(mouse_y - ball.y, mouse_x - ball.x)

        # Use the calculated power
        ball.speed_x = stick.power * math.cos(angle)
        ball.speed_y = stick.power * math.sin(angle)

        # Hide stick after shot
        stick.visible = False
        # Reset charge
        stick.reset_charge()
        # Reset shot ready flag
        shot_ready = False
        # Reset mouse press
        mouse_pressed = False

    # Draw everything
    draw_pool_table()
    ball.draw(screen)
    yellow_ball.draw(screen)
    red_ball.draw(screen)
    
    def are_all_balls_stopped(balls):
        return all(ball.speed_x == 0 and ball.speed_y == 0 for ball in balls if ball.in_game)
        
    if ball.speed_x == 0 and ball.speed_y == 0:
        # In the drawing section
        if are_all_balls_stopped([ball, yellow_ball, red_ball]) and ball.in_game:
            
            stick.visible = True
            # Pass angle to draw method for power indicator positioning
            mouse_x, mouse_y = mouse_pos
            angle = math.atan2(mouse_y - ball.y, mouse_x - ball.x)
            stick.draw(screen, ball, mouse_pos, angle)

    pygame.display.flip()
    pygame.time.Clock().tick(60)  # Limit to 60 FPS

pygame.quit()    
