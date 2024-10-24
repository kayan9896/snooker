import pygame
import math
from ball import Ball
from stick import Stick
import random
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
# Define ball colors
BALL_COLORS = {
    1: (255, 255, 0),        # Yellow
    2: (0, 0, 155),          # Blue
    3: (255, 0, 0),          # Dark Red
    4: (128, 0, 128),        # Purple
    5: (255, 140, 0),        # Orange
    6: (0, 100, 0),          # Dark Green
    7: (139, 69, 19),        # Brown
    8: (0, 0, 0),            # Black
    9: (255, 255, 0)         # Yellow (with white stripe - we'll add the stripe when drawing)
}

# Create the balls
balls = []
# Create cue ball
cue_ball = Ball(EDGE_WIDTH + (WIDTH-EDGE_WIDTH*2-POCKET_RADIUS*2)/8 * 2, 
                EDGE_WIDTH + buffer_height + BALL_RADIUS, 
                BALL_RADIUS, WHITE, WIDTH, HEIGHT, EDGE_WIDTH, POCKET_RADIUS, offset, 
                acceleration=0.05, resetable=True, number=0)  # number=0 for cue ball

# Calculate the foot spot position
foot_spot_x = WIDTH - EDGE_WIDTH - (WIDTH-EDGE_WIDTH*2-POCKET_RADIUS*2)/8 * 2
foot_spot_y = HEIGHT/2

# Function to create a ball with number
def create_numbered_ball(number, x, y):
    return Ball(x, y, BALL_RADIUS, BALL_COLORS[number], WIDTH, HEIGHT, EDGE_WIDTH, 
                POCKET_RADIUS, offset, acceleration=0.05, resetable=False, number=number)

# Create all numbered balls (1-9)
numbered_balls = [create_numbered_ball(i, 0, 0) for i in range(1, 10)]

def setup_rack():
    # Position for the apex ball (9 ball)
    apex_x = foot_spot_x
    apex_y = foot_spot_y
    ball_spacing = BALL_RADIUS * 2  # Slightly larger spacing to prevent overlapping

    # Calculate the total height needed for 5 balls
    total_height = ball_spacing * 4  # Space for 5 balls vertically
    start_y = apex_y - total_height/2  # Start from the top

    # Set the 9 ball position (center of the rack)
    numbered_balls[8].x = apex_x  # 9 ball (index 8)
    numbered_balls[8].y = apex_y  # Center position

    # Available balls for random placement (excluding 1 and 9)
    available_balls = numbered_balls[1:8]  # balls 2-8
    random.shuffle(available_balls)

    # Place two random balls in the same vertical line as 9 ball
    available_balls[0].x = apex_x
    available_balls[0].y = apex_y - ball_spacing  # One ball above 9
    available_balls[1].x = apex_x
    available_balls[1].y = apex_y + ball_spacing  # One ball below 9

    # Row offset for the diamond shape
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
    numbered_balls[0].x = apex_x - row_offset * 2  # 1 ball
    numbered_balls[0].y = apex_y  # Same height as 9 ball

    # Place remaining ball at the back right
    remaining_ball = available_balls[6]
    remaining_ball.x = apex_x + row_offset * 2
    remaining_ball.y = apex_y  # Same height as 9 ball

    
# Add stripe to 9 ball
def draw_ball_with_stripe(screen, ball):
    # Draw base ball
    pygame.draw.circle(screen, ball.color, (int(ball.x), int(ball.y)), ball.radius)

    if ball.number == 9:  # Add white stripe to 9 ball
        stripe_rect = pygame.Rect(
            ball.x - ball.radius,
            ball.y - ball.radius/3,
            ball.radius * 2,
            ball.radius * 2/3
        )
        pygame.draw.rect(screen, WHITE, stripe_rect)
        # Redraw the outline
        pygame.draw.circle(screen, ball.color, (int(ball.x), int(ball.y)), ball.radius, 1)

# Modify the main game loop to handle all balls
def are_all_balls_stopped(balls):
    return all(ball.speed_x == 0 and ball.speed_y == 0 for ball in balls if ball.in_game)


current_target_ball = 1

def check_foul(cue_ball, numbered_balls):
    global foul, current_target_ball
    foul = False

    if not cue_ball.in_game:
        foul = True
        print("Foul: Cue ball pocketed")
        return

    if not cue_ball.collision_order:
        foul = True
        print("Foul: No ball hit")
        return
    
    # Check if the first ball hit was the current target ball
    first_hit = cue_ball.collision_order[0]
    if first_hit.number != current_target_ball:
        foul = True
        print(f"Foul: Ball {current_target_ball} not hit first")

ball_left = 9  # Initialize at the start of the game

def handle_game_logic(cue_ball, numbered_balls):
    global game_over, foul, resetting_cue_ball, current_player, current_target_ball, ball_left

    check_foul(cue_ball, numbered_balls)

    # Check if any ball was pocketed by comparing current ball count with previous
    current_ball_count = sum(ball.in_game for ball in numbered_balls)
    any_ball_pocketed = current_ball_count < ball_left
    ball_left = current_ball_count

    # Clear collision orders
    cue_ball.collision_order.clear()
    for ball in numbered_balls:
        ball.collision_order.clear()

    if foul:
        current_player = 3 - current_player
        resetting_cue_ball = True
        # Spot the 9-ball if it was pocketed on a foul
        if not numbered_balls[8].in_game:
            numbered_balls[8].spot([cue_ball] + [b for b in numbered_balls if b.in_game])
    elif not numbered_balls[8].in_game:  # 9 ball legally pocketed
        game_over = True
        print("Game Over! Player", current_player, "wins!")
        reset_game(cue_ball, numbered_balls)
    else:
        # Update current_target_ball if the current target was pocketed
        if not numbered_balls[current_target_ball - 1].in_game:
            # Find next target ball
            for i in range(current_target_ball, 10):
                if i == 9 or numbered_balls[i - 1].in_game:
                    current_target_ball = i
                    print(f"New target ball: {current_target_ball}")
                    break

        # Switch player if no balls were pocketed on this shot
        if not any_ball_pocketed:
            current_player = 3 - current_player
            print(f"No balls pocketed. Switching to Player {current_player}")

    if not cue_ball.in_game:
        cue_ball.reset()

def reset_game(cue_ball, numbered_balls):
    global game_over, foul, resetting_cue_ball, current_player, current_target_ball, ball_left
    game_over = False
    foul = False
    resetting_cue_ball = False
    current_player = 1
    current_target_ball = 1
    ball_left = 9  # Reset ball count

    cue_ball.reset()
    for ball in numbered_balls:
        ball.reset()

    setup_rack()

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
    

setup_rack()  # Call this at the start of the game
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
                if is_valid_cue_position(mouse_x, mouse_y, cue_ball, numbered_balls):
                    cue_ball.x, cue_ball.y = mouse_x, mouse_y
                    ball_placement_confirmed = True
                    print("Ball placement confirmed")

            elif cue_ball.speed_x == 0 and cue_ball.speed_y == 0 and not resetting_cue_ball:
                # Shot preparation
                if cue_ball.in_game:
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

            elif mouse_pressed and cue_ball.speed_x == 0 and cue_ball.speed_y == 0 and not resetting_cue_ball:
                # Shot release
                mouse_pressed = False
                shot_ready = True

    # Get current mouse position
    mouse_pos = pygame.mouse.get_pos()

    # Update stick power if mouse is pressed
    if mouse_pressed and cue_ball.speed_x == 0 and cue_ball.speed_y == 0:
        # Calculate angle between ball and mouse for drawing and potential shot
        mouse_x, mouse_y = mouse_pos
        angle = math.atan2(mouse_y - cue_ball.y, mouse_x - cue_ball.x)

        # Update power
        stick.update_power()

        # Automatic shot release when max power is reached
        if stick.max_power_reached:
            shot_ready = True

    # Check if shot is ready to be released
    if shot_ready and cue_ball.speed_x == 0 and cue_ball.speed_y == 0 and not shot_taken:
        # Get current mouse position for shot direction
        mouse_x, mouse_y = mouse_pos

        # Calculate velocity based on opposite direction of stick
        angle = math.atan2(mouse_y - cue_ball.y, mouse_x - cue_ball.x)

        # Use the calculated power
        cue_ball.speed_x = stick.power * math.cos(angle)
        cue_ball.speed_y = stick.power * math.sin(angle)

        # Hide stick after shot
        stick.visible = False
        # Reset charge
        stick.reset_charge()
        # Reset shot ready flag
        shot_ready = False
        # Mark shot as taken
        shot_taken = True


    # Modify the drawing section:
    draw_pool_table()
    for ball in numbered_balls:
        if ball.number == 9:
            draw_ball_with_stripe(screen, ball)
        else:
            ball.draw(screen)
    cue_ball.draw(screen)

    # Update all balls
    cue_ball.move(numbered_balls)
    for ball in numbered_balls:
        ball.move([cue_ball] + [b for b in numbered_balls if b != ball])

    # Modify the game logic handling:
    if are_all_balls_stopped([cue_ball] + numbered_balls) and shot_taken:
        handle_game_logic(cue_ball, numbered_balls)
        shot_taken = False

    # Ball placement visualization during reset
    if resetting_cue_ball:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if is_valid_cue_position(mouse_x, mouse_y, cue_ball, numbered_balls):
            temp_surface = pygame.Surface((cue_ball.radius*2, cue_ball.radius*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, (200, 200, 200, 128), (cue_ball.radius, cue_ball.radius), cue_ball.radius)
            screen.blit(temp_surface, (mouse_x - cue_ball.radius, mouse_y - cue_ball.radius))

    # Draw stick when ball is stationary
    if cue_ball.speed_x == 0 and cue_ball.speed_y == 0 and not resetting_cue_ball:
        if are_all_balls_stopped([cue_ball]+numbered_balls) and cue_ball.in_game:
            stick.visible = True
            mouse_x, mouse_y = mouse_pos
            angle = math.atan2(mouse_y - cue_ball.y, mouse_x - cue_ball.x)
            stick.draw(screen, cue_ball, mouse_pos, angle)

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
