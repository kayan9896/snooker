import pygame
import math
import time

class Stick:
    def __init__(self, length=200, color=(102, 51, 0)):
        self.length = length
        self.color = color
        self.thickness = 4
        self.visible = True
        self.max_power = 25  # Maximum power of the shot
        self.min_power = 5   # Minimum power of the shot
        self.max_charge_time = 5  # Maximum time to reach full power (in seconds)
        self.power = self.min_power
        self.charge_start_time = 0
        self.max_power_reached = False  # Flag to track if max power is reached

    def start_charging(self):
        """Start charging the shot"""
        self.charge_start_time = time.time()
        self.power = self.min_power
        self.max_power_reached = False

    def update_power(self):
        """Update shot power based on charging time"""
        if self.charge_start_time > 0:
            # Calculate charge duration
            charge_duration = time.time() - self.charge_start_time

            # Interpolate power based on charge time
            if charge_duration >= self.max_charge_time:
                self.power = self.max_power
                self.max_power_reached = True
            else:
                # Linear interpolation of power
                self.power = self.min_power + (self.max_power - self.min_power) * (charge_duration / self.max_charge_time)

    def reset_charge(self):
        """Reset charging state"""
        self.charge_start_time = 0
        self.power = self.min_power
        self.max_power_reached = False
        

    def draw(self, screen, ball, mouse_pos, angle):
        if not self.visible:
            return

        # Calculate stick end points (opposite side of the ball from mouse)
        stick_start_x = ball.x - (self.length + ball.radius) * math.cos(angle)
        stick_start_y = ball.y - (self.length + ball.radius) * math.sin(angle)
        stick_end_x = ball.x - ball.radius * math.cos(angle)
        stick_end_y = ball.y - ball.radius * math.sin(angle)

        # Draw stick
        pygame.draw.line(screen, self.color,
                         (stick_start_x, stick_start_y),
                         (stick_end_x, stick_end_y),
                         self.thickness)

        # Draw power indicator near stick end
        power_indicator_length = 50

        # Calculate position for power indicator slightly offset from stick end
        offset = 10  # Pixels away from stick end
        indicator_x = stick_end_x + offset * abs(math.cos(angle + math.pi/2))+15
        indicator_y = stick_end_y + offset * math.sin(angle + math.pi/2)

        # Background of power indicator
        pygame.draw.rect(screen, (200, 200, 200), 
                         (indicator_x, indicator_y, 
                          power_indicator_length, 10))

        # Filled part of power indicator
        current_power_length = power_indicator_length * (self.power / self.max_power)
        pygame.draw.rect(screen, (255, 0, 0), 
                         (indicator_x, indicator_y, 
                          current_power_length, 10))
