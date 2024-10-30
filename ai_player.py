import math
import random

class AIPlayer:
    def __init__(self):
        self.difficulty = 1.0  # Can be adjusted for different difficulty levels
        self.top_spin = 0
        self.side_spin = 0

    def find_closest_pocket(self, ball_x, ball_y, pockets):
        """Find the closest pocket to a given ball position"""
        closest_pocket = None
        min_distance = float('inf')

        for pocket in pockets:
            distance = math.sqrt((pocket[0] - ball_x)**2 + (pocket[1] - ball_y)**2)
            if distance < min_distance:
                min_distance = distance
                closest_pocket = pocket

        return closest_pocket

    def calculate_shot_angle(self, cue_x, cue_y, target_x, target_y, pocket_x, pocket_y):
        """
        Calculate the angle needed to hit the target ball into the pocket.
        Uses the ghost ball method for accurate angle calculation.
        """
        # Calculate the angle between target ball and pocket
        target_to_pocket_angle = math.atan2(pocket_y - target_y, pocket_x - target_x)

        # Calculate the ghost ball position
        # This is where the cue ball needs to hit the target ball to direct it towards the pocket
        ghost_ball_distance = 2 * self.BALL_RADIUS  # Two ball radii from target ball center
        ghost_x = target_x - ghost_ball_distance * math.cos(target_to_pocket_angle)
        ghost_y = target_y - ghost_ball_distance * math.sin(target_to_pocket_angle)

        # Calculate the angle from cue ball to ghost ball position
        shot_angle = math.atan2(ghost_y - cue_y, ghost_x - cue_x)

        return shot_angle

    def is_shot_blocked(self, cue_x, cue_y, target_x, target_y, all_balls):
        """Check if there are any balls blocking the shot path"""
        shot_angle = math.atan2(target_y - cue_y, target_x - cue_x)
        shot_distance = math.sqrt((target_x - cue_x)**2 + (target_y - cue_y)**2)

        for ball in all_balls:
            if not ball.in_game or ball.number == 0:  # Skip cue ball and pocketed balls
                continue

            # Calculate perpendicular distance from ball to shot line
            dx = ball.x - cue_x
            dy = ball.y - cue_y
            dist_to_line = abs(dx * math.sin(shot_angle) - dy * math.cos(shot_angle))

            # Calculate how far along the shot line this ball is
            dist_along_line = dx * math.cos(shot_angle) + dy * math.sin(shot_angle)

            # Check if ball is between cue ball and target ball and close enough to block
            if dist_to_line < 2 * self.BALL_RADIUS and 0 < dist_along_line < shot_distance:
                return True

        return False

    def calculate_shot(self, cue_ball, target_ball, all_balls, pockets, BALL_RADIUS):
        """Calculate the best shot for the AI player"""
        if not target_ball.in_game:
            return None, None, 0, 0

        self.BALL_RADIUS = BALL_RADIUS  # Store for use in other methods

        # Find closest pocket to target ball
        closest_pocket = self.find_closest_pocket(target_ball.x, target_ball.y, pockets)

        # Calculate ideal shot angle to pocket the ball
        ideal_angle = self.calculate_shot_angle(
            cue_ball.x, cue_ball.y,
            target_ball.x, target_ball.y,
            closest_pocket[0], closest_pocket[1]
        )

        # Check if direct shot is blocked
        if self.is_shot_blocked(cue_ball.x, cue_ball.y, target_ball.x, target_ball.y, all_balls):
            # Could add bank shot calculation here
            # For now, just add more randomness to try to find a clear shot
            ideal_angle += random.uniform(-0.5, 0.5)

        # Add slight randomness based on difficulty
        angle = ideal_angle + random.uniform(-0.1, 0.1) * (1 - self.difficulty)

        # Calculate power based on distance
        distance = math.sqrt(
            (target_ball.x - cue_ball.x)**2 + 
            (target_ball.y - cue_ball.y)**2
        )

        # Adjust power based on distance to pocket
        pocket_distance = math.sqrt(
            (closest_pocket[0] - target_ball.x)**2 + 
            (closest_pocket[1] - target_ball.y)**2
        )

        # Use more power for longer shots, but not too much
        base_power = min(distance / 4, 15)
        power = base_power * (1 + pocket_distance / 400)  # Adjust multiplier as needed
        power = min(power * self.difficulty, 15)  # Cap maximum power

        # Add slight randomness to power
        power += random.uniform(-0.5, 0.5) * (1 - self.difficulty)

        # Calculate spin based on position
        self.top_spin = random.uniform(-0.03, 0.03)
        self.side_spin = random.uniform(-0.02, 0.02)

        return angle, power, self.top_spin, self.side_spin


        
    def find_legal_cue_ball_position(self, game_instance, is_initial_placement):
        """
        Find a legal position for the cue ball placement.
        Returns (x, y) coordinates for a valid position.
        """
        # Define the boundaries for ball placement
        if is_initial_placement:
            # For breaking shot: only in the "kitchen" area
            min_x = game_instance.EDGE_WIDTH + game_instance.buffer_HEIGHT + game_instance.BALL_RADIUS
            max_x = game_instance.EDGE_WIDTH + (game_instance.WIDTH - game_instance.EDGE_WIDTH*2 - 
                    game_instance.POCKET_RADIUS*2)/8 * 2
        else:
            # For regular placement: anywhere on the table
            min_x = game_instance.EDGE_WIDTH + game_instance.buffer_HEIGHT + game_instance.BALL_RADIUS
            max_x = game_instance.WIDTH - game_instance.EDGE_WIDTH - game_instance.buffer_HEIGHT - game_instance.BALL_RADIUS

        min_y = game_instance.EDGE_WIDTH + game_instance.buffer_HEIGHT + game_instance.BALL_RADIUS
        max_y = game_instance.TABLE_HEIGHT - game_instance.EDGE_WIDTH - game_instance.buffer_HEIGHT - game_instance.BALL_RADIUS

        # Try to find a strategic position
        target_ball = game_instance.numbered_balls[game_instance.current_target_ball - 1]
        if target_ball.in_game:
            # Try to place the cue ball with a good angle to the target ball
            attempts = 0
            while attempts < 50:  # Limit attempts to avoid infinite loop
                # Calculate a position that gives a good angle to the target ball
                if is_initial_placement:
                    # For breaking, try to get a centered position
                    suggested_x = (min_x + max_x) / 2
                    suggested_y = (min_y + max_y) / 2
                else:
                    # For regular placement, try to get a good angle to the target ball
                    # Start from a position slightly behind the target ball
                    angle = random.uniform(0, 2 * math.pi)
                    distance = random.uniform(150, 250)  # Adjustable distance
                    suggested_x = target_ball.x + distance * math.cos(angle)
                    suggested_y = target_ball.y + distance * math.sin(angle)

                # Clamp the suggested position to valid boundaries
                suggested_x = max(min_x, min(max_x, suggested_x))
                suggested_y = max(min_y, min(max_y, suggested_y))

                # Check if this position is valid
                if game_instance.is_valid_cue_position(
                    suggested_x, suggested_y, 
                    game_instance.cue_ball, 
                    game_instance.numbered_balls,
                    is_initial_placement
                ):
                    return suggested_x, suggested_y

                attempts += 1

        # If strategic placement fails or no target ball, use random placement
        max_attempts = 100
        attempt = 0
        while attempt < max_attempts:
            x = random.uniform(min_x, max_x)
            y = random.uniform(min_y, max_y)

            if game_instance.is_valid_cue_position(
                x, y, 
                game_instance.cue_ball, 
                game_instance.numbered_balls,
                is_initial_placement
            ):
                return x, y

            attempt += 1

        # If all attempts fail, return a default position
        return (min_x + 50, game_instance.TABLE_HEIGHT / 2)
