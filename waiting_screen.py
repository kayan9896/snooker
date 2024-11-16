import pygame
import time
from online import OnlineGameConnection

class WaitingScreen:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self.font = pygame.font.Font(None, 36)
        self.timeout = 30  # 30 seconds timeout
        self.connection = OnlineGameConnection()

    def draw(self, time_left):
        self.screen.fill((0, 0, 0))

        # Draw waiting message
        waiting_text = self.font.render("Waiting for opponent...", True, (255, 255, 255))
        timer_text = self.font.render(f"Time remaining: {time_left}s", True, (255, 255, 255))
        cancel_text = self.font.render("Press ESC to cancel", True, (255, 255, 255))

        self.screen.blit(waiting_text, 
                        (self.width//2 - waiting_text.get_width()//2, 
                         self.height//2 - 50))
        self.screen.blit(timer_text, 
                        (self.width//2 - timer_text.get_width()//2, 
                         self.height//2))
        self.screen.blit(cancel_text, 
                        (self.width//2 - cancel_text.get_width()//2, 
                         self.height//2 + 50))

        pygame.display.flip()

    def run(self):
        start_time = time.time()

        # Try to connect to server
        try:
            self.connection.connect()
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            return "menu"

        # Start looking for a match
        self.connection.find_match()

        while True:
            current_time = time.time()
            elapsed_time = current_time - start_time
            time_left = max(0, int(self.timeout - elapsed_time))

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.connection.disconnect()
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.connection.disconnect()
                        return "menu"

            # Check if match is found
            if self.connection.is_match_found():
                return "matched"

            # Check for timeout
            if time_left == 0:
                self.connection.disconnect()
                return "menu"

            self.draw(time_left)
            pygame.time.Clock().tick(60)
