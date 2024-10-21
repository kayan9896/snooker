import pygame

class Ball:
    def __init__(self, x, y, radius, color, width, height, edge_width, pocket_radius, offset, acceleration):
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

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def move(self):
        # Update speed based on acceleration
        self.speed_x = self.update_speed(self.speed_x, self.acceleration_x)
        self.speed_y = self.update_speed(self.speed_y, self.acceleration_y)

        self.x += self.speed_x
        self.y += self.speed_y

        # Check for pockets
        if self.check_pocket(self.edge_width + self.offset, self.edge_width + self.offset, self.pocket_radius):
            self.reset()
        elif self.check_pocket(self.width - self.edge_width - self.offset, self.edge_width + self.offset, self.pocket_radius):
            self.reset()
        elif self.check_pocket(self.edge_width + self.offset, self.height - self.edge_width - self.offset, self.pocket_radius):
            self.reset()
        elif self.check_pocket(self.width - self.edge_width - self.offset, self.height - self.edge_width - self.offset, self.pocket_radius):
            self.reset()
        elif self.check_pocket(self.width // 2, self.edge_width, self.pocket_radius+4):
            self.reset()
        elif self.check_pocket(self.width // 2, self.height - self.edge_width, self.pocket_radius+4):
            self.reset()

        
        # Check for collisions with buffers
        if self.x < self.edge_width + self.buffer_height + self.radius:
            self.speed_x = -self.speed_x

        elif self.x > self.width - self.edge_width - self.buffer_height - self.radius:
            self.speed_x = -self.speed_x

        if self.y < self.edge_width + self.buffer_height + self.radius:
            self.speed_y = -self.speed_y
        elif self.y > self.height - self.edge_width - self.buffer_height - self.radius:
            self.speed_y = -self.speed_y

        
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
        self.x = self.edge_width + (self.width - self.edge_width * 2 - self.pocket_radius * 2) / 8 * 2
        self.y = self.edge_width + self.pocket_radius + self.radius
        self.speed_x = 0
        self.speed_y = 0
