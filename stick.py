import pygame
import math
import time

class Stick:
    def __init__(self, length=200, color=(102, 51, 0)):
        self.length = length
        self.color = color
        self.thickness = 4
        self.visible = True
        self.max_power = 20
        self.min_power = 5
        self.max_charge_time = 5
        self.power = self.min_power
        self.charge_start_time = 0
        self.max_power_reached = False

        # New attributes for stick motion
        self.max_pullback = 50  # Maximum distance to pull back while charging
        self.current_pullback = 0
        self.striking = False
        self.strike_speed = 40  # Speed of the striking motion
        self.strike_position = 0
        self.strike_complete = False

    def start_charging(self):
        """Start charging the shot"""
        self.charge_start_time = time.time()
        self.power = self.min_power
        self.max_power_reached = False
        self.current_pullback = 0
        self.striking = False
        self.strike_complete = False

    def update_power(self):
        """Update shot power and stick pullback based on charging time"""
        if self.charge_start_time > 0:
            charge_duration = time.time() - self.charge_start_time

            if charge_duration >= self.max_charge_time:
                self.power = self.max_power
                self.max_power_reached = True
                self.current_pullback = self.max_pullback
            else:
                # Linear interpolation of power and pullback
                power_ratio = charge_duration / self.max_charge_time
                self.power = self.min_power + (self.max_power - self.min_power) * power_ratio
                self.current_pullback = self.max_pullback * power_ratio

    def start_strike(self):
        """Initialize the striking motion"""
        self.striking = True
        self.strike_position = self.current_pullback

    def update_strike(self):
        """Update the striking motion"""
        if self.striking and not self.strike_complete:
            self.strike_position -= self.strike_speed
            if self.strike_position <= 0:
                self.strike_complete = True
                self.striking = False
                self.visible = False

    def draw(self, screen, ball, mouse_pos, angle, portal):
        if not self.visible:
            return

        # Calculate stick position with pullback
        current_offset = self.current_pullback
        if self.striking:
            current_offset = self.strike_position

        # Calculate stick end points with pullback offset
        stick_start_x = ball.x - (self.length + ball.radius + current_offset) * math.cos(angle)
        stick_start_y = ball.y - (self.length + ball.radius + current_offset) * math.sin(angle)
        stick_end_x = ball.x - (ball.radius + current_offset) * math.cos(angle)
        stick_end_y = ball.y - (ball.radius + current_offset) * math.sin(angle)

        # Draw stick
        pygame.draw.line(screen, self.color,
                        (stick_start_x, stick_start_y),
                        (stick_end_x, stick_end_y),
                        self.thickness)

        # Draw power indicator vertically next to spin circle
        power_indicator_height = 100
        power_indicator_width = 20

        indicator_x = portal.spin_circle_center[0] + portal.SPIN_CIRCLE_RADIUS + 30
        indicator_y = portal.spin_circle_center[1] + power_indicator_height//2

        # Background of power indicator
        pygame.draw.rect(screen, (200, 200, 200), 
                        (indicator_x, indicator_y - power_indicator_height, 
                         power_indicator_width, power_indicator_height))

        # Filled part of power indicator
        current_power_height = power_indicator_height * (self.power / self.max_power)
        pygame.draw.rect(screen, (255, 0, 0), 
                        (indicator_x, 
                         indicator_y - current_power_height,
                         power_indicator_width, 
                         current_power_height))
