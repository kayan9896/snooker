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
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def move(self, other_balls=None):
        if not self.in_game:
            return

        # Update speed based on acceleration
        self.speed_x = self.update_speed(self.speed_x, self.acceleration_x)
        self.speed_y = self.update_speed(self.speed_y, self.acceleration_y)

        self.x += self.speed_x
        self.y += self.speed_y

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
            self.speed_x = -self.speed_x
        elif self.x > self.width - self.edge_width - self.buffer_height - self.radius:
            self.x = self.width - self.edge_width - self.buffer_height - self.radius
            self.speed_x = -self.speed_x

        if self.y < self.edge_width + self.buffer_height + self.radius:
            self.y = self.edge_width + self.buffer_height + self.radius
            self.speed_y = -self.speed_y
        elif self.y > self.height - self.edge_width - self.buffer_height - self.radius:
            self.y = self.height - self.edge_width - self.buffer_height - self.radius
            self.speed_y = -self.speed_y

    def check_ball_collision(self, other_ball):
        # Calculate distance between ball centers
        dx = other_ball.x - self.x
        dy = other_ball.y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        # Check if balls are colliding
        if distance <= (self.radius + other_ball.radius):
            if self.color==(255,255,255):
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
        self.in_game = True
        self.collision_order.clear()
