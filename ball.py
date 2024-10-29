import pygame
import math

class Ball:
    def __init__(self, x, y, radius, color, width, height, edge_width, pocket_radius, offset, acceleration, number=0):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed_x = 0.0
        self.speed_y = 0.0
        self.acceleration = acceleration
        self.acceleration_x = acceleration
        self.acceleration_y = acceleration
        self.width = width
        self.height = height
        self.edge_width = edge_width
        self.pocket_radius = pocket_radius
        self.offset = offset
        self.buffer_height = pocket_radius
        self.mass = 1  # Add mass for momentum calculations
        self.in_game = True  # New flag to control drawing and movement
        self.collision_order = []
        self.initial_x = x
        self.initial_y = y
        self.foot_spot_x = width - edge_width - (width - edge_width * 2 - pocket_radius * 2) / 8 * 2
        self.foot_spot_y = height / 2
        self.number=number
        self.top_spin = 0.0    # Range: -1.0 (back spin) to 1.0 (top spin)
        self.side_spin = 0.0   # Range: -1.0 (left spin) to 1.0 (right spin)
        self.spin_decay = 0.98 # Spin decay factor
        self.spin_effect_strength = 0.3 # Adjustable coefficient for spin effects
        self.rotational_speed_x = 0.0  # Rotational velocity in x direction
        self.rotational_speed_y = 0.0  # Rotational velocity in y direction
        self.sliding_acceleration = acceleration  # Sliding friction
        self.rotational_acceleration = acceleration * 0.2  # Much smaller for rotation
        self.initial_angle = 0.0  # Store initial direction of motion

        # Add new attributes for text rotation
        self.font = pygame.font.Font(None, int(radius * 1.5))
        self.number_angle = 0  # Current rotation angle of the number
        self.rotation_speed = 0  # Will be updated based on ball's speed

    def spot(self, other_balls):
        self.x = self.foot_spot_x
        self.y = self.foot_spot_y
        self.speed_x = 0
        self.speed_y = 0
        self.in_game = True
        self.collision_order.clear()

        # Check if the spot is occupied
        while any(((self.x - ball.x)**2 + (self.y - ball.y)**2) <= (2*self.radius)**2 for ball in other_balls if ball != self and ball.in_game):
            # Move the ball back towards the center of the table
            self.y -= self.radius
            if self.y < self.radius:  # If we've reached the top of the table
                self.y = self.height - self.radius  # Move to the bottom
                self.x -= self.radius  # and shift left

        # Ensure the ball is on the table
        self.x = max(self.edge_width + self.radius, min(self.x, self.width - self.edge_width - self.radius))
        self.y = max(self.edge_width + self.radius, min(self.y, self.height - self.edge_width - self.radius))

    

    def draw(self, screen):
        if self.in_game:
            # Draw the ball
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
            

            if self.number == 9:  # Add white stripe to 9 ball
                stripe_rect = pygame.Rect(
                    self.x - self.radius,
                    self.y - self.radius/3,
                    self.radius * 2,
                    self.radius * 2/3
                )
                pygame.draw.rect(screen, (0,0,0,32), stripe_rect)
                # Redraw the outline
                #pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius, 1)
                
            if self.number > 0:  # Don't draw number on cue ball
                # Update rotation based on ball's speed
                speed = math.sqrt(self.speed_x**2 + self.speed_y**2)
                self.rotation_speed = speed * 0.1  # Adjust this multiplier to change rotation speed
                self.number_angle += self.rotation_speed

                # Calculate number visibility based on rotation
                visibility = abs(math.cos(self.number_angle))

                if visibility > 0.3:  # Only draw if sufficiently visible
                    # Create number text
                    
                    number_text = self.font.render(str(self.number), True, (0, 0, 0))
                    number_rect = number_text.get_rect()

                    # Scale the text based on visibility
                    scaled_width = int(number_rect.width * visibility)
                    scaled_height = int(number_rect.height * visibility)
                    scaled_inner = int(self.radius/2 * visibility)
                    if scaled_width > 0 and scaled_height > 0 and scaled_inner>0:  # Prevent scaling to 0
                        scaled_text = pygame.transform.scale(number_text, (scaled_width, scaled_height))
                        pygame.draw.circle(screen, (255,255,255), (int(self.x), int(self.y)), scaled_inner)

                        # Position the number in the center of the ball
                        text_rect = scaled_text.get_rect(center=(int(self.x), int(self.y)))

                        # Draw the number
                        screen.blit(scaled_text, text_rect)

            
                

    def apply_spin_effects(self):
        if not self.in_game:
            return

        # Handle top/back spin as before
        if self.top_spin != 0 and self.rotational_speed_x == 0 and self.rotational_speed_y == 0:
            velocity_mag = math.sqrt(self.speed_x**2 + self.speed_y**2)
            if velocity_mag > 0:
                self.initial_angle = math.atan2(self.speed_y, self.speed_x)
                rotational_magnitude = abs(self.top_spin) * 3
                self.rotational_speed_x = rotational_magnitude * math.cos(self.initial_angle)
                self.rotational_speed_y = rotational_magnitude * math.sin(self.initial_angle)
                if self.top_spin < 0:
                    self.rotational_speed_x *= -1
                    self.rotational_speed_y *= -1
                self.top_spin=0

        # Handle side spin
        # Handle side spin - initial deflection when speed is first applied
        velocity_mag = math.sqrt(self.speed_x**2 + self.speed_y**2)
        if velocity_mag > 0 and self.side_spin != 0:
            if not hasattr(self, 'initial_target_angle'):
                # Store the initial target angle when spin is first applied
                self.initial_target_angle = math.atan2(self.speed_y, self.speed_x)

                # Apply initial deflection
                deflection_angle = math.asin(self.side_spin) # Adjust for initial deflection
                # Negative side spin (left) starts right of target line
                # Positive side spin (right) starts left of target line
                new_angle = self.initial_target_angle - deflection_angle
                print(deflection_angle,self.speed_x,self.speed_y)
                # Set new velocity direction while maintaining magnitude
                self.speed_x = velocity_mag * math.cos(new_angle)
                self.speed_y = velocity_mag * math.sin(new_angle)
                print(self.speed_x,self.speed_y)
            else:
                # Calculate current angle
                current_angle = math.atan2(self.speed_y, self.speed_x)

                # Calculate angle to target line
                angle_to_target = self.initial_target_angle - current_angle

                # Apply curve force toward target line
                curve_strength = 0.05  # Adjust for curve intensity

                # Apply rotational force to curve back to target line
                rotation_angle = curve_strength * math.asin(self.side_spin)
                new_speed_x = self.speed_x * math.cos(rotation_angle) - self.speed_y * math.sin(rotation_angle)
                new_speed_y = self.speed_x * math.sin(rotation_angle) + self.speed_y * math.cos(rotation_angle)

                # Normalize to maintain speed
                current_mag = math.sqrt(new_speed_x**2 + new_speed_y**2)
                self.speed_x = new_speed_x * velocity_mag / current_mag
                self.speed_y = new_speed_y * velocity_mag / current_mag
        else: 
            if hasattr(self, 'initial_target_angle'): del self.initial_target_angle


    def move(self, other_balls=None):
        if not self.in_game:
            return

        self.apply_spin_effects()
        
        # Update translational speeds with sliding friction
        velocity_mag = math.sqrt(self.speed_x**2 + self.speed_y**2)
        if velocity_mag > 0:
            angle = math.atan2(self.speed_y, self.speed_x)
            acc_x = self.sliding_acceleration * abs(math.cos(angle))
            acc_y = self.sliding_acceleration * abs(math.sin(angle))
            self.speed_x = self.update_speed(self.speed_x, acc_x)
            self.speed_y = self.update_speed(self.speed_y, acc_y)

        # Update rotational speeds with rotational friction
        rotational_mag = math.sqrt(self.rotational_speed_x**2 + self.rotational_speed_y**2)
        if rotational_mag > 0:
            rot_acc_x = self.rotational_acceleration * abs(math.cos(self.initial_angle))
            rot_acc_y = self.rotational_acceleration * abs(math.sin(self.initial_angle))
            self.rotational_speed_x = self.update_speed(self.rotational_speed_x, rot_acc_x)
            self.rotational_speed_y = self.update_speed(self.rotational_speed_y, rot_acc_y)

        # Update position using both translational and rotational velocities
        self.x += self.speed_x + self.rotational_speed_x
        self.y += self.speed_y + self.rotational_speed_y

        # Check for collisions with other balls before moving
        if other_balls:
            for ball in other_balls:
                if ball != self and ball.in_game:
                        self.check_ball_collision(ball)


        # Update acceleration based on current speed
        angle = math.atan2(self.speed_y, self.speed_x)
        self.acceleration_x = self.acceleration * abs(math.cos(angle))
        self.acceleration_y = self.acceleration * abs(math.sin(angle))

        # Check for pockets
        pocket_check_points = [
            (self.edge_width + self.offset, self.edge_width + self.offset),
            (self.width - self.edge_width - self.offset, self.edge_width + self.offset),
            (self.edge_width + self.offset, self.height - self.edge_width - self.offset),
            (self.width - self.edge_width - self.offset, self.height - self.edge_width - self.offset),
            (self.width // 2, self.edge_width),
            (self.width // 2, self.height - self.edge_width)
        ]

        for x, y in pocket_check_points:
            if self.check_pocket(x, y, self.pocket_radius + 8):
                self.in_game = False  # Remove the ball from the game
                break

        # Check for collisions with buffers
        if self.x < self.edge_width + self.buffer_height + self.radius:
            self.x = self.edge_width + self.buffer_height + self.radius
            self.speed_x = -self.speed_x  # Normal rebound
            if self.side_spin != 0:
                # Add velocity in the direction parallel to the rail (y direction)
                self.speed_y -= self.side_spin*3 * abs(self.speed_x)  # More spin effect for faster hits
                self.side_spin*=0.3
            self.rotational_speed_x = -self.rotational_speed_x
            # Update initial angle to reflect new rotation direction
            self.initial_angle = math.pi - self.initial_angle



        elif self.x > self.width - self.edge_width - self.buffer_height - self.radius:
            self.x = self.width - self.edge_width - self.buffer_height - self.radius
            self.speed_x = -self.speed_x
            if self.side_spin != 0:
                self.speed_y += self.side_spin *3* abs(self.speed_x)
                self.side_spin*=0.3
            self.rotational_speed_x = -self.rotational_speed_x
            self.initial_angle = math.pi - self.initial_angle

        if self.y < self.edge_width + self.buffer_height + self.radius:
            self.y = self.edge_width + self.buffer_height + self.radius
            self.speed_y = -self.speed_y
            if self.side_spin != 0:
                self.speed_x += self.side_spin *3* abs(self.speed_y)
                self.side_spin*=0.3
            self.rotational_speed_y = -self.rotational_speed_y
            # Update initial angle to reflect new rotation direction
            self.initial_angle = -self.initial_angle

        elif self.y > self.height - self.edge_width - self.buffer_height - self.radius:
            self.y = self.height - self.edge_width - self.buffer_height - self.radius
            self.speed_y = -self.speed_y
            if self.side_spin != 0:
                self.speed_x -= self.side_spin *3* abs(self.speed_y)
                self.side_spin*=0.3
            self.rotational_speed_y = -self.rotational_speed_y
            self.initial_angle = -self.initial_angle

        # Optional: Add some energy loss during buffer collision
        buffer_absorption = 0.8  # Adjust this value to control energy loss
        if self.x <= self.edge_width + self.buffer_height + self.radius or \
           self.x >= self.width - self.edge_width - self.buffer_height - self.radius or \
           self.y <= self.edge_width + self.buffer_height + self.radius or \
           self.y >= self.height - self.edge_width - self.buffer_height - self.radius:
            self.rotational_speed_x *= buffer_absorption
            self.rotational_speed_y *= buffer_absorption


    def check_ball_collision(self, other_ball):
        # Calculate distance between ball centers
        dx = other_ball.x - self.x
        dy = other_ball.y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        # Check if balls are colliding
        if distance <= (self.radius + other_ball.radius):
            if self.color==(255,255,255):

                # Transfer some spin to the target ball
                spin_transfer = 0.3  # 30% spin transfer
                other_ball.top_spin = self.top_spin * spin_transfer
                other_ball.side_spin = self.side_spin * spin_transfer

                # Reduce cue ball spin after collision
                self.top_spin *= (1 - spin_transfer)
                self.side_spin *= (1 - spin_transfer)

                self.collision_order.append(other_ball)
                other_ball.collision_order.append(self)
                print([i.color for i in self.collision_order])
            # Calculate collision angle
            angle = math.atan2(dy, dx)

            # Calculate initial velocities
            v1x = self.speed_x
            v1y = self.speed_y
            v2x = other_ball.speed_x
            v2y = other_ball.speed_y

            # Decompose velocities along the collision axis and perpendicular to it
            v1_parallel = v1x * math.cos(angle) + v1y * math.sin(angle)
            v1_perpendicular = -v1x * math.sin(angle) + v1y * math.cos(angle)
            v2_parallel = v2x * math.cos(angle) + v2y * math.sin(angle)
            v2_perpendicular = -v2x * math.sin(angle) + v2y * math.cos(angle)

            # Calculate new velocities using conservation of momentum and kinetic energy
            new_v1_parallel = ((self.mass - other_ball.mass) * v1_parallel + 2 * other_ball.mass * v2_parallel) / (self.mass + other_ball.mass)
            new_v2_parallel = ((other_ball.mass - self.mass) * v2_parallel + 2 * self.mass * v1_parallel) / (self.mass + other_ball.mass)

            # Reconstruct velocities
            self.speed_x = new_v1_parallel * math.cos(angle) - v1_perpendicular * math.sin(angle)
            self.speed_y = new_v1_parallel * math.sin(angle) + v1_perpendicular * math.cos(angle)
            other_ball.speed_x = new_v2_parallel * math.cos(angle) - v2_perpendicular * math.sin(angle)
            other_ball.speed_y = new_v2_parallel * math.sin(angle) + v2_perpendicular * math.cos(angle)

            # After calculating new velocities, modify them based on spin
            if abs(self.side_spin) > 0:
                # Deflection angle modified by side spin
                spin_deflection = self.side_spin * 0.2
                deflection_angle = math.atan2(self.speed_y, self.speed_x) + spin_deflection
                velocity_mag = math.sqrt(self.speed_x**2 + self.speed_y**2)
                self.speed_x = velocity_mag * math.cos(deflection_angle)
                self.speed_y = velocity_mag * math.sin(deflection_angle)

            # Transfer some spin to the other ball
            other_ball.top_spin += self.top_spin * 0.3
            other_ball.side_spin += self.side_spin * 0.3

            # Reduce spin after collision
            self.top_spin *= 0.7
            self.side_spin *= 0.7


            # Update acceleration based on new velocities
            angle1 = math.atan2(self.speed_y, self.speed_x)
            self.acceleration_x = self.acceleration * abs(math.cos(angle1))
            self.acceleration_y = self.acceleration * abs(math.sin(angle1))

            angle2 = math.atan2(other_ball.speed_y, other_ball.speed_x)
            other_ball.acceleration_x = other_ball.acceleration * abs(math.cos(angle2))
            other_ball.acceleration_y = other_ball.acceleration * abs(math.sin(angle2))

            # Separate balls to prevent sticking
            overlap = self.radius + other_ball.radius - distance+0.01
            self.x -= overlap/2 * math.cos(angle)
            self.y -= overlap/2 * math.sin(angle)
            other_ball.x += overlap/2 * math.cos(angle)
            other_ball.y += overlap/2 * math.sin(angle)



    def check_pocket(self, x, y, radius):
        return (self.x - x) ** 2 + (self.y - y) ** 2 <= radius ** 2

    def update_speed(self, speed, acceleration):
        if speed > 0:
            return max(0, speed - acceleration)
        elif speed < 0:
            return min(0, speed + acceleration)
        else:
            return 0

    def reset(self):
        self.x = self.initial_x
        self.y = self.initial_y
        self.speed_x = 0
        self.speed_y = 0
        self.rotational_speed_x = 0.0  
        self.rotational_speed_y = 0.0 
        self.in_game = True
        self.collision_order.clear()
