import math
import random

class AIPlayer:
    def __init__(self):
        self.difficulty = 2  # Can be adjusted for different difficulty levels
        self.top_spin = 0
        self.side_spin = 0
        self.pockets = []  # Will be populated when calculate_shot is called
        self.WIDTH, self.TABLE_HEIGHT = 800, 400
        self.HEIGHT = 600
        self.EDGE_WIDTH = 20
        self.POCKET_RADIUS = 15
        self.DIAMOND_SIZE = 5
        self.BALL_RADIUS = 8

    def calculate_shot(self, cue_ball, target_ball, all_balls, pockets, BALL_RADIUS):
        """Calculate the best shot for the AI player"""
        if not target_ball.in_game:
            return None, None, 0, 0

        self.BALL_RADIUS = BALL_RADIUS
        self.pockets = pockets

        # Evaluate best pocket and direct shot
        best_pocket, pocket_score = self.evaluate_pocket_shots(cue_ball, target_ball, pockets, all_balls)

        if best_pocket and pocket_score > 0:
            # Check if direct path to target is blocked
            direct_blocked = self.is_shot_blocked(
                cue_ball.x, cue_ball.y, 
                target_ball.x, target_ball.y, 
                [ball for ball in all_balls if ball != target_ball]
            )

            #if not direct_blocked:
                # Try direct shot only if path is clear
            direct_shot = self.evaluate_direct_shot(cue_ball, target_ball, best_pocket, all_balls)
            if direct_shot:
                shot_params, direct_score = direct_shot
                print(direct_score)
                if direct_score > 0.1:  # Good direct shot threshold
                    return shot_params

            # If direct shot is blocked or not good enough, try bank shots
            bank_shot = self.try_bank_shots(cue_ball, target_ball, all_balls, pockets)
            if bank_shot:
                shot_params, bank_score = bank_shot
                return shot_params  # Always take bank shot if available when direct is blocked

        # If no good shots found, play safe
        return self.calculate_safety_shot(cue_ball, target_ball, all_balls)


    def evaluate_pocket_shots(self, cue_ball, target_ball, pockets, all_balls):
        """Evaluate all possible pocket shots considering distance and angle"""
        best_pocket = None
        best_score = float('-inf')
        MAX_ANGLE_THRESHOLD = math.radians(75)  # Maximum preferred angle
        IDEAL_ANGLE_THRESHOLD = math.radians(45)  # Ideal maximum angle

        for pocket in pockets:
            # Calculate distances
            target_to_pocket_dist = math.sqrt(
                (pocket[0] - target_ball.x)**2 + 
                (pocket[1] - target_ball.y)**2
            )

            # Calculate angles
            cue_to_target_angle = math.atan2(
                target_ball.y - cue_ball.y,
                target_ball.x - cue_ball.x
            )
            target_to_pocket_angle = math.atan2(
                pocket[1] - target_ball.y,
                pocket[0] - target_ball.x
            )

            # Calculate absolute angle difference
            angle_diff = abs(((target_to_pocket_angle - cue_to_target_angle + math.pi) 
                            % (2 * math.pi)) - math.pi)

            # Score based on distance
            distance_score = 1.0 - (target_to_pocket_dist / 1000)

            # Score based on angle
            if angle_diff > MAX_ANGLE_THRESHOLD:
                angle_score = 0.2  # Severe penalty for difficult angles
            elif angle_diff > IDEAL_ANGLE_THRESHOLD:
                angle_score = 1.0 - ((angle_diff - IDEAL_ANGLE_THRESHOLD) / 
                                   (MAX_ANGLE_THRESHOLD - IDEAL_ANGLE_THRESHOLD) * 0.5)
            else:
                angle_score = 1.0

            # Check if path to pocket is blocked
            target_to_pocket_blocked = self.is_shot_blocked(
                target_ball.x, target_ball.y,
                pocket[0], pocket[1],
                [ball for ball in all_balls if ball != target_ball]
            )

            # Calculate final score
            if target_to_pocket_blocked:
                final_score = -1
            else:
                final_score = (distance_score * 0.4 + angle_score * 0.6)

            if final_score > best_score:
                best_score = final_score
                best_pocket = pocket

        return best_pocket, best_score

    def evaluate_direct_shot(self, cue_ball, target_ball, pocket, all_balls):
        """Evaluate a direct shot to a pocket"""
        ideal_angle = self.calculate_shot_angle(
            cue_ball.x, cue_ball.y,
            target_ball.x, target_ball.y,
            pocket[0], pocket[1]
        )

        # Calculate cut angle
        cut_angle = abs(math.atan2(
            pocket[1] - target_ball.y,
            pocket[0] - target_ball.x
        ) - math.atan2(
            target_ball.y - cue_ball.y,
            target_ball.x - cue_ball.x
        ))
        cut_angle = min(cut_angle, math.pi - cut_angle)

        # Reject extremely difficult cuts
        if cut_angle > math.radians(75):
            return None

        # Check if shot is blocked
        if self.is_shot_blocked(cue_ball.x, cue_ball.y, target_ball.x, target_ball.y, all_balls):
            return None

        # Calculate distances
        distance_to_target = math.sqrt(
            (target_ball.x - cue_ball.x)**2 + 
            (target_ball.y - cue_ball.y)**2
        )
        target_to_pocket = math.sqrt(
            (pocket[0] - target_ball.x)**2 + 
            (pocket[1] - target_ball.y)**2
        )

        # Score the shot
        score = 1.0
        score -= (distance_to_target + target_to_pocket) / 1000
        score -= cut_angle / math.pi

        # Calculate power
        power = min((distance_to_target + target_to_pocket/2) / 4, 15) * self.difficulty

        return (ideal_angle, power, 0, 0), score

    def try_bank_shots(self, cue_ball, target_ball, all_balls, pockets):
        """Calculate bank shots using geometric symmetry"""
        best_bank_shot = None
        best_bank_score = float('-inf')

        # Define cushions with offset
        offset = self.BALL_RADIUS * 1.5
        top_cushion = self.EDGE_WIDTH + offset
        bottom_cushion = self.TABLE_HEIGHT - self.EDGE_WIDTH - offset
        left_cushion = self.EDGE_WIDTH + offset
        right_cushion = self.WIDTH - self.EDGE_WIDTH - offset

        # Try each pocket
        for pocket in self.pockets:
            # Calculate symmetric points for each cushion
            symmetric_points = [
                (target_ball.x, top_cushion - (target_ball.y - top_cushion)),  # Top
                (target_ball.x, bottom_cushion + (bottom_cushion - target_ball.y)),  # Bottom
                (left_cushion - (target_ball.x - left_cushion), target_ball.y),  # Left
                (right_cushion + (right_cushion - target_ball.x), target_ball.y)  # Right
            ]
            cushions = [
                ("top", top_cushion),
                ("bottom", bottom_cushion),
                ("left", left_cushion),
                ("right", right_cushion)
            ]

            for (cushion_type, cushion_pos), symmetric_point in zip(cushions, symmetric_points):
                intersection = self.find_cushion_intersection(
                    cue_ball, symmetric_point, cushion_type, cushion_pos
                )

                if intersection:
                    x_int, y_int = intersection

                    if (left_cushion <= x_int <= right_cushion and 
                        top_cushion <= y_int <= bottom_cushion):

                        if (not self.is_shot_blocked(cue_ball.x, cue_ball.y, x_int, y_int, all_balls) and
                            not self.is_shot_blocked(x_int, y_int, target_ball.x, target_ball.y, all_balls)):

                            angle = math.atan2(y_int - cue_ball.y, x_int - cue_ball.x)
                            distance_to_cushion = math.sqrt(
                                (x_int - cue_ball.x)**2 + (y_int - cue_ball.y)**2
                            )
                            distance_to_target = math.sqrt(
                                (target_ball.x - x_int)**2 + (target_ball.y - y_int)**2
                            )

                            score = self.score_bank_shot(
                                distance_to_cushion, distance_to_target,
                                target_ball, pocket
                            )

                            if score > best_bank_score:
                                total_distance = distance_to_cushion + distance_to_target
                                power = min(total_distance / 3, 15) * 1.2 * self.difficulty

                                best_bank_score = score
                                best_bank_shot = (angle, power, 0, 0)

        if best_bank_shot:
            return best_bank_shot, best_bank_score
        return None

    def find_cushion_intersection(self, cue_ball, symmetric_point, cushion_type, cushion_pos):
        """Find intersection point of shot line with cushion"""
        if cushion_type in ["top", "bottom"]:
            if cue_ball.y == symmetric_point[1]:
                return None
            t = (cushion_pos - cue_ball.y) / (symmetric_point[1] - cue_ball.y)
            x_int = cue_ball.x + t * (symmetric_point[0] - cue_ball.x)
            return (x_int, cushion_pos)
        else:  # Left or right cushion
            if cue_ball.x == symmetric_point[0]:
                return None
            t = (cushion_pos - cue_ball.x) / (symmetric_point[0] - cue_ball.x)
            y_int = cue_ball.y + t * (symmetric_point[1] - cue_ball.y)
            return (cushion_pos, y_int)

    def score_bank_shot(self, distance_to_cushion, distance_to_target, target_ball, pocket):
        """Score a bank shot based on various factors"""
        score = 0.4  # Base score for bank shots
        total_distance = distance_to_cushion + distance_to_target
        score -= total_distance / 1000

        target_to_pocket_dist = math.sqrt(
            (pocket[0] - target_ball.x)**2 + (pocket[1] - target_ball.y)**2
        )
        score -= target_to_pocket_dist / 800

        return score

    def calculate_shot_angle(self, cue_x, cue_y, target_x, target_y, pocket_x, pocket_y):
        """Calculate the angle needed to hit the target ball into the pocket"""
        target_to_pocket_angle = math.atan2(pocket_y - target_y, pocket_x - target_x)
        ghost_ball_distance = 2 * self.BALL_RADIUS
        ghost_x = target_x - ghost_ball_distance * math.cos(target_to_pocket_angle)
        ghost_y = target_y - ghost_ball_distance * math.sin(target_to_pocket_angle)
        return math.atan2(ghost_y - cue_y, ghost_x - cue_x)

    def is_shot_blocked(self, start_x, start_y, end_x, end_y, all_balls):
        """Check if there are any balls blocking the shot path"""
        shot_angle = math.atan2(end_y - start_y, end_x - start_x)
        shot_distance = math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
        SHOT_PATH_TOLERANCE = self.BALL_RADIUS * 1.8

        for ball in all_balls:
            if not ball.in_game:
                continue

            dx = ball.x - start_x
            dy = ball.y - start_y
            dist_to_line = abs(dx * math.sin(shot_angle) - dy * math.cos(shot_angle))
            dist_along_line = dx * math.cos(shot_angle) + dy * math.sin(shot_angle)

            if dist_to_line < SHOT_PATH_TOLERANCE and 0 < dist_along_line < shot_distance:
                return True

        return False

    def calculate_safety_shot(self, cue_ball, target_ball, all_balls):
        """Calculate a safety shot when no good offensive shot is available"""
        # Simple safety shot logic - hit softly towards a safe position
        angle = math.atan2(target_ball.y - cue_ball.y, target_ball.x - cue_ball.x)
        return angle, 5 * self.difficulty, 0, 0  # Low power safety shot

        
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
