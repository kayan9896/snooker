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

def are_all_balls_stopped(balls):
    return all(ball.speed_x == 0 and ball.speed_y == 0 for ball in balls if ball.in_game)

def check_foul(cue_ball, ball_3, ball_9):
    global foul
    foul = False

    if not cue_ball.in_game:
        foul = True
        print("Foul: Cue ball pocketed")
    elif not cue_ball.collision_order:
        foul = True
        print("Foul: No ball hit")
    elif ball_3.in_game and cue_ball.collision_order[0] != ball_3:
        foul = True
        print("Foul: 3 ball not hit first")
    elif ball_9 in cue_ball.collision_order and ball_3 in cue_ball.collision_order:
        if cue_ball.collision_order.index(ball_9) < cue_ball.collision_order.index(ball_3):
            foul = True
            print("Foul: 9 ball hit before 3 ball")
            

def handle_game_logic(cue_ball, ball_3, ball_9):
    global game_over, foul, resetting_cue_ball, current_player

    check_foul(cue_ball, ball_3, ball_9)

    # Reset collision data
    cue_ball.collision_order.clear()
    ball_3.collision_order.clear()
    ball_9.collision_order.clear()

    if foul:
        resetting_cue_ball = True
        if not ball_9.in_game:
            ball_9.spot([cue_ball, ball_3])  # Spot the 9-ball if it was pocketed on a foul
    elif not ball_9.in_game:
        game_over = True
        print("Game Over! Player", current_player, "wins!")
        reset_game(cue_ball, ball_3, ball_9)
    else:
        current_player = 3 - current_player  # Switch player if no foul and game not over

    # Always reset the cue ball if it's not in game (pocketed)
    if not cue_ball.in_game:
        cue_ball.reset()
        
def reset_game(cue_ball, ball_3, ball_9):
    global game_over, foul, resetting_cue_ball, current_player
    game_over = False
    foul = False
    resetting_cue_ball = False
    current_player = 1
    cue_ball.reset()
    ball_3.reset()
    ball_9.reset()

def is_valid_cue_position(x, y, cue_ball, other_balls):
    if (x < EDGE_WIDTH + cue_ball.radius or 
        x > WIDTH - EDGE_WIDTH - cue_ball.radius or 
        y < EDGE_WIDTH + cue_ball.radius or 
        y > HEIGHT - EDGE_WIDTH - cue_ball.radius):
        return False

    for ball in other_balls:
        if ball.in_game:
            distance = math.sqrt((x - ball.x)**2 + (y - ball.y)**2)
            if distance < cue_ball.radius + ball.radius:
                return False

    return True
    

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
shot_ready = False
resetting_cue_ball = False
ball_placement_confirmed = False
shot_taken = False
current_player = 1
foul = False
game_over = False

# Main game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            if resetting_cue_ball:
                # Ball placement logic
                if is_valid_cue_position(mouse_x, mouse_y, ball, [yellow_ball, red_ball]):
                    ball.x, ball.y = mouse_x, mouse_y
                    ball_placement_confirmed = True
                    print("Ball placement confirmed")

            elif ball.speed_x == 0 and ball.speed_y == 0 and not resetting_cue_ball:
                # Shot preparation
                if ball.in_game:
                    mouse_pressed = True
                    stick.start_charging()

        elif event.type == pygame.MOUSEBUTTONUP:
            if resetting_cue_ball and ball_placement_confirmed:
                # Confirm ball placement
                resetting_cue_ball = False
                ball_placement_confirmed = False
                foul = False
                shot_taken = False
                print("Ready to shoot")

            elif mouse_pressed and ball.speed_x == 0 and ball.speed_y == 0 and not resetting_cue_ball:
                # Shot release
                mouse_pressed = False
                shot_ready = True

    # Get current mouse position
    mouse_pos = pygame.mouse.get_pos()

    # Update ball positions
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
    if shot_ready and ball.speed_x == 0 and ball.speed_y == 0 and not shot_taken:
        # Get current mouse position for shot direction
        mouse_x, mouse_y = mouse_pos

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
        # Mark shot as taken
        shot_taken = True

    # Check for game logic after all balls have stopped
    if are_all_balls_stopped([ball, yellow_ball, red_ball]) and shot_taken:
        handle_game_logic(ball, red_ball, yellow_ball)
        shot_taken = False

    # Draw everything
    draw_pool_table()
    ball.draw(screen)
    yellow_ball.draw(screen)
    red_ball.draw(screen)

    # Ball placement visualization during reset
    if resetting_cue_ball:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if is_valid_cue_position(mouse_x, mouse_y, ball, [yellow_ball, red_ball]):
            temp_surface = pygame.Surface((ball.radius*2, ball.radius*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, (200, 200, 200, 128), (ball.radius, ball.radius), ball.radius)
            screen.blit(temp_surface, (mouse_x - ball.radius, mouse_y - ball.radius))

    # Draw stick when ball is stationary
    if ball.speed_x == 0 and ball.speed_y == 0 and not resetting_cue_ball:
        if are_all_balls_stopped([ball, yellow_ball, red_ball]) and ball.in_game:
            stick.visible = True
            mouse_x, mouse_y = mouse_pos
            angle = math.atan2(mouse_y - ball.y, mouse_x - ball.x)
            stick.draw(screen, ball, mouse_pos, angle)

    # Display current player and foul status
    font = pygame.font.Font(None, 36)
    player_text = font.render(f"Player {current_player}", True, (255, 255, 255))
    screen.blit(player_text, (10, 10))
    if foul:
        foul_text = font.render("FOUL", True, (255, 0, 0))
        screen.blit(foul_text, (WIDTH - 100, 10))

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
