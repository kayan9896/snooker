import pygame
import math

class Stick:
    def __init__(self, length=200, color=(102, 51, 0)):
        self.length = length
        self.color = color
        self.thickness = 4
        self.visible = True

    def draw(self, screen, ball, mouse_pos):
        if not self.visible:
            return

        # Calculate angle between ball and mouse
        dx = mouse_pos[0] - ball.x
        dy = mouse_pos[1] - ball.y
        angle = math.atan2(dy, dx)

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
