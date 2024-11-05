import math
import random

class AIPlayer:
    def __init__(self):
        self.difficulty = 1  # Can be adjusted for different difficulty levels
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
        """Modified to properly handle blocked shots and legal safeties"""
        if not target_ball.in_game:
            return None, None, 0, 0

        self.BALL_RADIUS = BALL_RADIUS
        self.pockets = pockets

        # Check if direct path to target is blocked
        direct_blocked = self.is_shot_blocked(
            cue_ball.x, cue_ball.y, 
            target_ball.x, target_ball.y, 
            [ball for ball in all_balls if ball != target_ball]
        )

        best_shot = None
        best_score = float('-inf')

        if not direct_blocked:
            # Try direct shots if path is clear
            for pocket in pockets:
                shot_eval = self.evaluate_direct_shot(cue_ball, target_ball, pocket, all_balls)
                if shot_eval:
                    shot_params, score = shot_eval
                    if score > best_score:
                        best_score = score
                        best_shot = shot_params

            # If direct path available but not great, try safety
            if best_score < 1.4:
                safety_shot = self.calculate_direct_safety(cue_ball, target_ball, all_balls)
                if safety_shot:
                    print(6)
                    return safety_shot

        else:
            # If direct path is blocked, try bank shots
            bank_shot = self.try_bank_shots(cue_ball, target_ball, all_balls, pockets)
            if bank_shot:
                bank_params, bank_score = bank_shot
                if bank_score > best_score:
                    best_score = bank_score
                    best_shot = bank_params

            # If no good bank shot, try bank safety
            if best_score < 0.3:
                bank_safety = self.calculate_bank_safety(cue_ball, target_ball, all_balls)
                if bank_safety:
                    return bank_safety

        return best_shot if best_shot else self.calculate_bank_safety(cue_ball, target_ball, all_balls)

    def calculate_direct_safety(self, cue_ball, target_ball, all_balls):
        """Calculate a safety shot when direct path is available"""
        best_shot = None
        best_score = float('-inf')

        # Base angle to target ball
        base_angle = math.atan2(
            target_ball.y - cue_ball.y,
            target_ball.x - cue_ball.x
        )

        # Try different slight variations of the angle
        for angle_offset in [0]:
            shot_angle = base_angle + angle_offset

            # Calculate where the target ball will go after impact
            target_direction = shot_angle + math.pi

            # Try different powers
            for power in [8, 10, 12]:  # Medium power for control but enough to reach
                # Estimate target ball's final position
                target_travel = power * 6
                target_final_x = target_ball.x + target_travel * math.cos(target_direction)
                target_final_y = target_ball.y + target_travel * math.sin(target_direction)

                # Keep within table boundaries
                target_final_x = max(self.EDGE_WIDTH + self.BALL_RADIUS,
                                   min(self.WIDTH - self.EDGE_WIDTH - self.BALL_RADIUS,
                                       target_final_x))
                target_final_y = max(self.EDGE_WIDTH + self.BALL_RADIUS,
                                   min(self.TABLE_HEIGHT - self.EDGE_WIDTH - self.BALL_RADIUS,
                                       target_final_y))

                score = self.evaluate_safety_position(target_final_x, target_final_y, 
                                                   cue_ball, target_ball, all_balls)

                if score > best_score:
                    best_score = score
                    best_shot = (shot_angle, power, 0, 0)

        return best_shot

    def calculate_bank_safety(self, cue_ball, target_ball, all_balls):
        """Calculate a bank safety shot when direct path is blocked"""
        best_shot = None
        best_score = float('-inf')

        # Define cushions
        cushions = [
            ("top", self.EDGE_WIDTH),
            ("bottom", self.TABLE_HEIGHT - self.EDGE_WIDTH),
            ("left", self.EDGE_WIDTH),
            ("right", self.WIDTH - self.EDGE_WIDTH)
        ]

        for cushion_type, cushion_pos in cushions:
            # Calculate possible bank shots off this cushion
            bank_points = self.calculate_bank_points(cue_ball, target_ball, cushion_type, cushion_pos)

            for bank_point in bank_points:
                # Check if bank shot path is clear
                if not self.is_shot_blocked(cue_ball.x, cue_ball.y, bank_point[0], bank_point[1],
                                          [b for b in all_balls if b != target_ball]):

                    shot_angle = math.atan2(bank_point[1] - cue_ball.y,
                                          bank_point[0] - cue_ball.x)

                    # Calculate post-impact trajectory
                    impact_angle = math.atan2(target_ball.y - bank_point[1],
                                            target_ball.x - bank_point[0])

                    # Try different powers
                    for power in [12, 14, 16]:  # Need more power for bank shots
                        target_travel = power * 4
                        target_final_x = target_ball.x + target_travel * math.cos(impact_angle)
                        target_final_y = target_ball.y + target_travel * math.sin(impact_angle)

                        # Keep within boundaries
                        target_final_x = max(self.EDGE_WIDTH + self.BALL_RADIUS,
                                           min(self.WIDTH - self.EDGE_WIDTH - self.BALL_RADIUS,
                                               target_final_x))
                        target_final_y = max(self.EDGE_WIDTH + self.BALL_RADIUS,
                                           min(self.TABLE_HEIGHT - self.EDGE_WIDTH - self.BALL_RADIUS,
                                               target_final_y))

                        score = self.evaluate_safety_position(target_final_x, target_final_y,
                                                           cue_ball, target_ball, all_balls)

                        if score > best_score:
                            best_score = score
                            best_shot = (shot_angle, power, 0, 0)

        return best_shot

    def calculate_bank_points(self, cue_ball, target_ball, cushion_type, cushion_pos):
        """Calculate possible bank points for a cushion"""
        bank_points = []

        if cushion_type in ["top", "bottom"]:
            # Mirror the target ball across the cushion
            mirrored_y = (2 * cushion_pos - target_ball.y 
                         if cushion_type == "top" 
                         else 2 * cushion_pos - target_ball.y)
            bank_points.append((target_ball.x, mirrored_y))
        else:
            # Mirror the target ball across the cushion
            mirrored_x = (2 * cushion_pos - target_ball.x 
                         if cushion_type == "left" 
                         else 2 * cushion_pos - target_ball.x)
            bank_points.append((mirrored_x, target_ball.y))

        return bank_points

    def evaluate_safety_position(self, final_x, final_y, cue_ball, target_ball, all_balls):
        """Evaluate the safety position with improved scoring"""
        score = 1.0

        # Prefer positions that:
        # 1. Are far from pockets but not impossible angles
        for pocket in self.pockets:
            dist = math.sqrt((final_x - pocket[0])**2 + (final_y - pocket[1])**2)
            angle = abs(math.atan2(pocket[1] - final_y, pocket[0] - final_x))
            # Want distance but not impossible angles
            pocket_score = (dist / 400) * (1 - abs(math.sin(angle)))
            score += pocket_score

        # 2. Are near cushions but not frozen
        cushion_dist = min(
            abs(final_x - self.EDGE_WIDTH),
            abs(final_x - (self.WIDTH - self.EDGE_WIDTH)),
            abs(final_y - self.EDGE_WIDTH),
            abs(final_y - (self.TABLE_HEIGHT - self.EDGE_WIDTH))
        )
        # Want close to cushion but not frozen
        if cushion_dist < self.BALL_RADIUS:
            score -= 0.5
        else:
            score += (1 - cushion_dist / 100) * 0.3

        # 3. Leave a reasonable distance from the cue ball
        safe_distance = math.sqrt((final_x - cue_ball.x)**2 + (final_y - cue_ball.y)**2)
        score += min(safe_distance / 300, 1.0) * 0.4

        return score


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

    def predict_cue_ball_destination(self, cue_ball, target_ball, pocket, angle, power):
        """Predict where the cue ball will end up after the shot"""
        # Simplified physics simulation
        contact_point = self.calculate_ball_contact_point(cue_ball, target_ball, angle)

        # Vector from contact point to pocket
        target_to_pocket = (
            pocket[0] - contact_point[0],
            pocket[1] - contact_point[1]
        )
        target_to_pocket_angle = math.atan2(target_to_pocket[1], target_to_pocket[0])

        # Estimate cue ball deflection
        deflection_angle = target_to_pocket_angle + math.pi / 2  # 90-degree deflection

        # Estimate travel distance based on power
        travel_distance = power * 10  # Adjust this factor based on your game physics

        # Calculate estimated final position
        estimated_x = contact_point[0] + travel_distance * math.cos(deflection_angle)
        estimated_y = contact_point[1] + travel_distance * math.sin(deflection_angle)

        # Account for table boundaries
        estimated_x = max(self.EDGE_WIDTH, min(self.WIDTH - self.EDGE_WIDTH, estimated_x))
        estimated_y = max(self.EDGE_WIDTH, min(self.TABLE_HEIGHT - self.EDGE_WIDTH, estimated_y))

        return estimated_x, estimated_y

    def calculate_ball_contact_point(self, cue_ball, target_ball, angle):
        """Calculate the point where the cue ball contacts the target ball"""
        distance = 2 * self.BALL_RADIUS
        return (
            target_ball.x - distance * math.cos(angle),
            target_ball.y - distance * math.sin(angle)
        )
    
    
    def evaluate_direct_shot(self, cue_ball, target_ball, pocket, all_balls):
        """Evaluate a direct shot considering cue ball control and next shot"""
        ideal_angle = self.calculate_shot_angle(
            cue_ball.x, cue_ball.y,
            target_ball.x, target_ball.y,
            pocket[0], pocket[1]
        )

        # Calculate initial shot difficulty
        cut_angle = abs(math.atan2(
            pocket[1] - target_ball.y,
            pocket[0] - target_ball.x
        ) - math.atan2(
            target_ball.y - cue_ball.y,
            target_ball.x - cue_ball.x
        ))
        cut_angle = min(cut_angle, math.pi - cut_angle)
        if cut_angle > math.radians(75):
            return None

        # Calculate distances and base power
        distance_to_target = math.sqrt(
            (target_ball.x - cue_ball.x)**2 + 
            (target_ball.y - cue_ball.y)**2
        )
        target_to_pocket = math.sqrt(
            (pocket[0] - target_ball.x)**2 + 
            (pocket[1] - target_ball.y)**2
        )
        base_power = min((distance_to_target + target_to_pocket/2) / 4, 20) * self.difficulty

        # Try different power levels
        best_shot = None
        best_score = float('-inf')
        power_levels = [base_power * 0.8, base_power, base_power * 1.2]

        for power in power_levels:
            # Predict cue ball destination
            estimated_x, estimated_y = self.predict_cue_ball_destination(
                cue_ball, target_ball, pocket, ideal_angle, power
            )

            # Score the current shot
            current_shot_score = 1.0
            current_shot_score -= (distance_to_target + target_to_pocket) / 10000
            current_shot_score -= cut_angle / math.pi

            # Consider next shot
            next_target = self.get_next_target_ball(target_ball, all_balls)
            if next_target:
                next_shot_options = self.evaluate_shot_options(
                    estimated_x, estimated_y, next_target, all_balls
                )
                next_shot_score = max([score for _, score in next_shot_options] or [0])
            else:
                next_shot_score = 0

            # Combine scores
            total_score = current_shot_score * 0.7 + next_shot_score * 0.3

            # Penalize shots where cue ball might be potted
            if self.is_cue_ball_potted_risk(estimated_x, estimated_y, self.pockets):
                total_score -= 2

            if total_score > best_score:
                best_score = total_score
                best_shot = (ideal_angle, power, 0, 0)

        if best_shot and best_score > 0.1:  # Only return if it's a decent shot
            return best_shot, best_score
        return None

    def is_cue_ball_potted_risk(self, x, y, pockets, risk_radius=30):
        """Check if the cue ball is at risk of being potted"""
        for pocket in pockets:
            distance = math.sqrt((x - pocket[0])**2 + (y - pocket[1])**2)
            if distance < risk_radius:
                return True
        return False

    def get_next_target_ball(self, current_target, all_balls):
        """Get the next target ball in order"""
        current_number = current_target.number
        next_number = current_number + 1
        for ball in all_balls:
            if ball.number == next_number and ball.in_game:
                return ball
        return None

    def evaluate_shot_options(self, cue_x, cue_y, target_ball, all_balls):
        """Evaluate shot options for a given cue ball position and target"""
        shot_options = []
        for pocket in self.pockets:
            # Check direct shots
            direct_shot = self.evaluate_direct_shot_simple(
                cue_x, cue_y, target_ball, pocket, all_balls
            )
            if direct_shot:
                shot_options.append(direct_shot)

            # Check bank shots
            bank_shot = self.try_bank_shots_simple(
                cue_x, cue_y, target_ball, all_balls, [pocket]
            )
            if bank_shot:
                shot_options.append(bank_shot)

        return shot_options

    def evaluate_direct_shot_simple(self, cue_x, cue_y, target_ball, pocket, all_balls):
        """Simplified direct shot evaluation for future shot consideration"""
        angle = self.calculate_shot_angle(
            cue_x, cue_y,
            target_ball.x, target_ball.y,
            pocket[0], pocket[1]
        )

        # Check if shot is blocked
        if self.is_shot_blocked(cue_x, cue_y, target_ball.x, target_ball.y, all_balls):
            return None

        # Simple scoring based on distance and angle
        distance = math.sqrt((cue_x - target_ball.x)**2 + (cue_y - target_ball.y)**2)
        score = 1.0 - (distance / 1000)

        return (angle, 10, 0, 0), score

    def try_bank_shots_simple(self, cue_x, cue_y, target_ball, all_balls, pockets):
        """Simplified bank shot evaluation"""
        best_bank_shot = None
        best_bank_score = float('-inf')

        # Define cushions with offset
        offset = self.POCKET_RADIUS / math.sqrt(2)
        top_cushion = self.EDGE_WIDTH + offset
        bottom_cushion = self.TABLE_HEIGHT - self.EDGE_WIDTH - offset
        left_cushion = self.EDGE_WIDTH + offset
        right_cushion = self.WIDTH - self.EDGE_WIDTH - offset

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

        temp_cue_ball = type('CueBall', (), {'x': cue_x, 'y': cue_y})

        for (cushion_type, cushion_pos), symmetric_point in zip(cushions, symmetric_points):
            intersection = self.find_cushion_intersection(
                temp_cue_ball, symmetric_point, cushion_type, cushion_pos
            )

            if intersection:
                x_int, y_int = intersection

                if (left_cushion <= x_int <= right_cushion and 
                    top_cushion <= y_int <= bottom_cushion):

                    distance = (math.sqrt((x_int - cue_x)**2 + (y_int - cue_y)**2) + 
                              math.sqrt((target_ball.x - x_int)**2 + (target_ball.y - y_int)**2))
                    score = 0.5 - (distance / 2000)

                    if score > best_bank_score:
                        best_bank_score = score
                        angle = math.atan2(y_int - cue_y, x_int - cue_x)
                        best_bank_shot = (angle, 15, 0, 0)

        if best_bank_shot:
            return best_bank_shot, best_bank_score
        return None

    def try_bank_shots(self, cue_ball, target_ball, all_balls, pockets):
        """Calculate bank shots using geometric symmetry"""
        best_bank_shot = None
        best_bank_score = float('-inf')

        # Define cushions with offset
        offset = self.POCKET_RADIUS / math.sqrt(2)
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
                                power = min(total_distance / 3, 20) * self.difficulty

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
        """Calculate a legal safety shot that hits the target ball first"""
        best_shot = None
        best_score = float('-inf')

        # First, check if we can hit the target ball
        if self.is_shot_blocked(
            cue_ball.x, cue_ball.y,
            target_ball.x, target_ball.y,
            [ball for ball in all_balls if ball != target_ball]
        ):
            return self.calculate_basic_safety(cue_ball, target_ball)

        # Calculate base angle to target ball
        base_angle = math.atan2(
            target_ball.y - cue_ball.y,
            target_ball.x - cue_ball.x
        )

        # Try different angles around the target ball
        for angle_offset in [0]:
            shot_angle = base_angle + angle_offset

            # Calculate where the target ball would go
            impact_point = self.calculate_ball_contact_point(cue_ball, target_ball, shot_angle)
            target_direction = shot_angle + math.pi  # Direction after impact

            # Try different powers for each angle
            for power in [5, 7, 9]:  # Low power options for better control
                # Estimate target ball's final position
                target_travel = power * 5  # Adjust this factor based on your physics
                target_final_x = target_ball.x + target_travel * math.cos(target_direction)
                target_final_y = target_ball.y + target_travel * math.sin(target_direction)

                # Keep within table boundaries
                target_final_x = max(self.EDGE_WIDTH + self.BALL_RADIUS,
                                   min(self.WIDTH - self.EDGE_WIDTH - self.BALL_RADIUS,
                                       target_final_x))
                target_final_y = max(self.EDGE_WIDTH + self.BALL_RADIUS,
                                   min(self.TABLE_HEIGHT - self.EDGE_WIDTH - self.BALL_RADIUS,
                                       target_final_y))

                # Score the safety shot
                score = self.evaluate_safety_position(
                    target_final_x, target_final_y,
                    cue_ball, target_ball,
                    all_balls
                )

                if score > best_score:
                    best_score = score
                    best_shot = (shot_angle, power, 0, 0)

        return best_shot if best_shot else self.calculate_basic_safety(cue_ball, target_ball)

    

    def calculate_hiding_safety(self, cue_ball, target_ball, all_balls):
        """Calculate a safety shot that hides the target ball behind other balls"""
        best_shot = None
        best_score = float('-inf')

        # Look for potential blocking balls
        for blocking_ball in all_balls:
            if not blocking_ball.in_game or blocking_ball == target_ball:
                continue

            # Calculate angles to position target ball behind blocking ball
            angles_to_try = [
                math.atan2(blocking_ball.y - target_ball.y, blocking_ball.x - target_ball.x) + offset
                for offset in [-0.2, 0, 0.2]  # Try slight variations
            ]

            for angle in angles_to_try:
                # Calculate where the target ball would end up
                target_final_x = blocking_ball.x - 2.2 * self.BALL_RADIUS * math.cos(angle)
                target_final_y = blocking_ball.y - 2.2 * self.BALL_RADIUS * math.sin(angle)

                # Calculate required shot angle and power
                shot_angle = math.atan2(target_final_y - target_ball.y,
                                      target_final_x - target_ball.x)
                distance = math.sqrt((target_final_x - target_ball.x)**2 + 
                                   (target_final_y - target_ball.y)**2)
                power = min(distance / 4, 10)  # Soft shot

                # Check if shot is possible
                if not self.is_shot_blocked(cue_ball.x, cue_ball.y,
                                          target_ball.x, target_ball.y,
                                          [b for b in all_balls if b != target_ball]):
                    # Score the shot based on how well it hides the target
                    score = self.evaluate_hiding_position(
                        target_final_x, target_final_y,
                        blocking_ball.x, blocking_ball.y,
                        all_balls
                    )

                    if score > best_score:
                        best_score = score
                        best_shot = (shot_angle, power, 0, 0)

        return best_shot

    def calculate_cushion_safety(self, cue_ball, target_ball, all_balls):
        """Calculate a safety shot that leaves the target ball near a cushion"""
        best_shot = None
        best_score = float('-inf')

        # Define cushion positions to try
        cushions = [
            (self.EDGE_WIDTH + self.BALL_RADIUS, target_ball.y),  # Left cushion
            (self.WIDTH - self.EDGE_WIDTH - self.BALL_RADIUS, target_ball.y),  # Right cushion
            (target_ball.x, self.EDGE_WIDTH + self.BALL_RADIUS),  # Top cushion
            (target_ball.x, self.TABLE_HEIGHT - self.EDGE_WIDTH - self.BALL_RADIUS)  # Bottom cushion
        ]

        for cushion_x, cushion_y in cushions:
            # Calculate shot parameters
            shot_angle = math.atan2(cushion_y - target_ball.y,
                                  cushion_x - target_ball.x)
            distance = math.sqrt((cushion_x - target_ball.x)**2 + 
                               (cushion_y - target_ball.y)**2)
            power = min(distance / 4, 12)  # Moderate power

            # Score based on position difficulty
            score = self.evaluate_cushion_position(cushion_x, cushion_y, all_balls)

            if score > best_score:
                best_score = score
                best_shot = (shot_angle, power, 0, 0)

        return best_shot

    def calculate_distance_safety(self, cue_ball, target_ball, all_balls):
        """Calculate a safety shot that maximizes the distance between balls"""
        best_shot = None
        best_score = float('-inf')

        # Try different angles
        for angle in range(0, 360, 20):
            rad_angle = math.radians(angle)

            # Calculate potential target position
            distance = 150  # Decent distance
            target_x = target_ball.x + distance * math.cos(rad_angle)
            target_y = target_ball.y + distance * math.sin(rad_angle)

            # Keep within table boundaries
            target_x = max(self.EDGE_WIDTH + self.BALL_RADIUS,
                          min(self.WIDTH - self.EDGE_WIDTH - self.BALL_RADIUS, target_x))
            target_y = max(self.EDGE_WIDTH + self.BALL_RADIUS,
                          min(self.TABLE_HEIGHT - self.EDGE_WIDTH - self.BALL_RADIUS, target_y))

            score = self.evaluate_distance_position(target_x, target_y, cue_ball, all_balls)

            if score > best_score:
                best_score = score
                shot_angle = math.atan2(target_y - target_ball.y,
                                      target_x - target_ball.x)
                best_shot = (shot_angle, 10, 0, 0)  # Moderate power

        return best_shot

    def evaluate_hiding_position(self, target_x, target_y, blocker_x, blocker_y, all_balls):
        """Score how well a position hides the target ball"""
        score = 1.0

        # Check if position is valid (not overlapping with other balls)
        for ball in all_balls:
            if ball.in_game:
                dist = math.sqrt((target_x - ball.x)**2 + (target_y - ball.y)**2)
                if dist < 2 * self.BALL_RADIUS:
                    return float('-inf')

        # Score based on how well the ball is hidden
        blocking_angle = math.atan2(blocker_y - target_y, blocker_x - target_x)

        # Check visibility from different angles
        visible_angles = 0
        for angle in range(0, 360, 20):
            rad_angle = math.radians(angle)
            if abs(rad_angle - blocking_angle) > math.pi/6:  # If angle is not blocked
                visible_angles += 1

        score -= visible_angles / 18  # Penalize based on how visible the ball is
        return score

    def evaluate_cushion_position(self, x, y, all_balls):
        """Score how difficult a cushion position is"""
        score = 1.0

        # Prefer positions that make it difficult to hit the ball directly
        for pocket in self.pockets:
            angle = abs(math.atan2(pocket[1] - y, pocket[0] - x))
            score += 0.1 * (math.pi/2 - abs(angle % (math.pi/2)))  # Prefer awkward angles

        # Penalize if position is too easy to hit
        clearance = min(
            abs(x - self.EDGE_WIDTH),
            abs(x - (self.WIDTH - self.EDGE_WIDTH)),
            abs(y - self.EDGE_WIDTH),
            abs(y - (self.TABLE_HEIGHT - self.EDGE_WIDTH))
        )
        score += 0.2 * (1 - clearance / 100)  # Prefer tight cushion positions

        return score

    def evaluate_distance_position(self, x, y, cue_ball, all_balls):
        """Score a position based on distance and difficulty"""
        score = 1.0

        # Prefer positions far from the cue ball
        distance = math.sqrt((x - cue_ball.x)**2 + (y - cue_ball.y)**2)
        score += distance / 500

        # Prefer positions that make the next shot difficult
        for pocket in self.pockets:
            angle = math.atan2(pocket[1] - y, pocket[0] - x)
            score += 0.1 * abs(angle % (math.pi/2))  # Prefer awkward angles

        return score

    def calculate_basic_safety(self, cue_ball, target_ball):
        """Basic safety shot that ensures hitting the target ball"""
        # Calculate direct angle to target ball
        angle = math.atan2(target_ball.y - cue_ball.y,
                          target_ball.x - cue_ball.x)

        # Use very low power to maintain control
        return angle, 5, 0, 0


    def find_legal_cue_ball_position(self, game_instance, is_initial_placement):
        """
        Find a strategic position for the cue ball placement using a scoring system.
        """
        # Define boundaries
        min_x = game_instance.EDGE_WIDTH + game_instance.buffer_HEIGHT + game_instance.BALL_RADIUS
        max_x = (game_instance.EDGE_WIDTH + (game_instance.WIDTH - game_instance.EDGE_WIDTH*2 - 
                 game_instance.POCKET_RADIUS*2)/8 * 2) if is_initial_placement else (
                 game_instance.WIDTH - game_instance.EDGE_WIDTH - game_instance.buffer_HEIGHT - 
                 game_instance.BALL_RADIUS)
        min_y = game_instance.EDGE_WIDTH + game_instance.buffer_HEIGHT + game_instance.BALL_RADIUS
        max_y = (game_instance.TABLE_HEIGHT - game_instance.EDGE_WIDTH - game_instance.buffer_HEIGHT - 
                 game_instance.BALL_RADIUS)

        best_position = None
        best_score = float('-inf')
        target_ball = game_instance.numbered_balls[game_instance.current_target_ball - 1]

        if not target_ball.in_game:
            return self.find_random_valid_position(game_instance, min_x, max_x, min_y, max_y, 
                                                 is_initial_placement)

        # Grid search for best position
        grid_steps = 20
        x_step = (max_x - min_x) / grid_steps
        y_step = (max_y - min_y) / grid_steps

        for i in range(grid_steps):
            for j in range(grid_steps):
                x = min_x + i * x_step
                y = min_y + j * y_step

                if not game_instance.is_valid_cue_position(
                    x, y, game_instance.cue_ball, game_instance.numbered_balls, is_initial_placement
                ):
                    continue

                score = self.evaluate_position(x, y, target_ball, game_instance)

                if score > best_score:
                    best_score = score
                    best_position = (x, y)

        if best_position:
            return best_position

        return self.find_random_valid_position(game_instance, min_x, max_x, min_y, max_y, 
                                             is_initial_placement)

    def evaluate_position(self, x, y, target_ball, game_instance):
        """
        Evaluate a potential cue ball position based on multiple factors.
        """
        score = 0
    
        # Distance to target ball (prefer medium distance)
        distance_to_target = math.sqrt((x - target_ball.x)**2 + (y - target_ball.y)**2)
        IDEAL_DISTANCE = 200  # Adjust this value based on your table size
        distance_score = 1 - abs(distance_to_target - IDEAL_DISTANCE) / IDEAL_DISTANCE
        score += distance_score * 0.3
    
        # Angle relative to pockets (prefer positions that allow straight shots)
        angle_score = 0
        for pocket in game_instance.pockets:
            target_to_pocket = math.atan2(pocket[1] - target_ball.y, 
                                        pocket[0] - target_ball.x)
            cue_to_target = math.atan2(target_ball.y - y, target_ball.x - x)
            angle_diff = abs(((target_to_pocket - cue_to_target + math.pi) % (2 * math.pi)) - math.pi)
    
            # Prefer smaller angles (straighter shots)
            pocket_score = 1 - (angle_diff / math.pi)
            angle_score = max(angle_score, pocket_score)
    
        score += angle_score * 0.3
    
        # Center table control (slight preference for positions near center)
        center_x = game_instance.WIDTH / 2
        center_y = game_instance.TABLE_HEIGHT / 2
        distance_to_center = math.sqrt((x - center_x)**2 + (y - center_y)**2)
        center_score = 1 - (distance_to_center / (game_instance.WIDTH / 2))
        score += center_score * 0.2
    
        # Check if shot is blocked
        blocked_penalty = 0
        for ball in game_instance.numbered_balls:
            if ball.in_game and ball != target_ball:
                if self.is_shot_blocked(x, y, target_ball.x, target_ball.y, [ball]):
                    blocked_penalty = 0.5
                    break
    
        score -= blocked_penalty
    
        return score
    
    def find_random_valid_position(self, game_instance, min_x, max_x, min_y, max_y, is_initial_placement):
        """
        Find a random valid position as a fallback.
        """
        max_attempts = 100
        for _ in range(max_attempts):
            x = random.uniform(min_x, max_x)
            y = random.uniform(min_y, max_y)
    
            if game_instance.is_valid_cue_position(
                x, y, game_instance.cue_ball, game_instance.numbered_balls, is_initial_placement
            ):
                return x, y
    
        return (min_x + 50, game_instance.TABLE_HEIGHT / 2)
