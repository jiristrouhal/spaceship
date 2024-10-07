import pygame  # type: ignore
import sys
import random
import math
from datetime import datetime

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
GRAVITY = 0.05
THRUST = 0.1
FUEL_CONSUMPTION = 1
ROTATION_SPEED = 2
FPS = 60
DT = 0.25


INIT_X = 50
INIT_Y = HEIGHT // 2
INIT_X_SPEED = 2
INIT_Y_SPEED = 0
INIT_ANGLE = 90


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)

# Load images
spaceship_image = pygame.image.load('images/spaceship.png')
spaceship_thrust_image = pygame.image.load('images/spaceship_thrust.png')

# Spaceship class
class Spaceship:
    def __init__(self):
        self.original_image = pygame.transform.scale(spaceship_image, (50, 50))
        self.original_thrust_image = pygame.transform.scale(spaceship_thrust_image, (50, 50))
        self.image = self.original_image
        self.thrust_image = self.original_thrust_image
        self.rect = self.image.get_rect(center=(INIT_X, INIT_Y))
        self.position = pygame.math.Vector2(self.rect.center)
        self.velocity = pygame.math.Vector2(INIT_X_SPEED, INIT_Y_SPEED)
        self.angle = INIT_ANGLE
        self.fuel = 1000.0
        self.thrusting = False

    def update(self, keys):
        self.thrusting = False
        if self.fuel > 0:
            if keys[pygame.K_UP]:
                thrust_vector = pygame.math.Vector2(0.0, -THRUST).rotate(-self.angle)
                self.velocity += DT*thrust_vector
                self.fuel -= FUEL_CONSUMPTION
                self.thrusting = True
            if keys[pygame.K_LEFT]:
                self.angle += DT*ROTATION_SPEED
            if keys[pygame.K_RIGHT]:
                self.angle -= DT*ROTATION_SPEED

        # Apply gravity
        self.velocity.y += DT*GRAVITY

        # Update position
        self.position.x += DT*self.velocity.x
        self.position.y += DT*self.velocity.y

        self.rect.x = self.position.x
        self.rect.y = self.position.y

        # Rotate the image
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.thrust_image = pygame.transform.rotate(self.original_thrust_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        # Boundary conditions
        if self.rect.left < 0:
            self.rect.left = 0
            self.velocity.x = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.velocity.x = 0
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity.y = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.velocity.y = 0

    def draw(self, screen):
        if self.thrusting:
            screen.blit(self.thrust_image, self.rect.topleft)
        else:
            screen.blit(self.image, self.rect.topleft)


def write_results(fuel, speed, height, success: str):
    with open('results.txt', 'a') as f:
        t = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f'Time: {t}, Fuel: {fuel:.2f}, Speed: {speed:.2f}, Height: {height:.2f}, {success}\n')

# Main game function
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Spaceship Game")
    clock = pygame.time.Clock()

    # Initialize font
    font = pygame.font.SysFont(None, 36)

    def reset_game():
        spaceship = Spaceship()
        landing_site_x = random.randint(0, WIDTH - 50)
        return spaceship, True, landing_site_x

    spaceship, running, landing_site_x = reset_game()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and not running:
                if event.key == pygame.K_SPACE:
                    spaceship, running, landing_site_x = reset_game()

        speed = math.sqrt(spaceship.velocity.x**2 + spaceship.velocity.y**2)
        height = HEIGHT - spaceship.rect.center[1] - 28

        screen.fill(BLACK)

        if running:
            keys = pygame.key.get_pressed()
            spaceship.update(keys)

            # Check for landing or crash
            if height <= 1:
                running = False

        else:
            if speed < 1:
                if landing_site_x <= spaceship.rect.centerx <= landing_site_x + 50:
                    text = "Successful landing!"
                    message = font.render("Successful landing!", True, GREEN)
                else:
                    text = "You missed the landing site!"
                    message = font.render("You missed the landing site!", True, ORANGE)
            else:
                text = "Crash!"
                message = font.render("Crash!", True, RED)

            write_results(spaceship.fuel, speed, height, text)

            screen.blit(message, (WIDTH // 2 - message.get_width() // 2, HEIGHT // 2 - message.get_height() // 2))
            retry_message = font.render("Press spacebar to try again", True, WHITE)
            screen.blit(retry_message, (WIDTH // 2 - retry_message.get_width() // 2, HEIGHT // 2 + message.get_height()))

        pygame.draw.line(screen, WHITE, (0, HEIGHT - 10), (WIDTH, HEIGHT - 10), 5)  # Draw the planet surface as a white line
        pygame.draw.line(screen, RED, (landing_site_x, HEIGHT - 10), (landing_site_x + 50, HEIGHT - 10), 5)  # Draw the landing site as a red line
        spaceship.draw(screen)

        # Render fuel text
        fuel_text = font.render(f"Fuel: {int(spaceship.fuel)}", True, WHITE)
        screen.blit(fuel_text, (10, 10))

        # Render speed magnitude text
        speed_text = font.render(f'Speed: {speed:.2f}', True, RED if speed>1.0 else WHITE)
        screen.blit(speed_text, (10, 50))

        # Render height text
        height_text = font.render(f'Height: {height:.2f}', True, WHITE)
        screen.blit(height_text, (10, 90))

        pygame.display.flip()
        clock.tick(FPS)



if __name__ == "__main__":
    main()
