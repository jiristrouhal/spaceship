import pygame  # type: ignore
import sys
import random
import math
from datetime import datetime
import os
import json

# Initialize Pygame
pygame.init()

# Constants
FPS = 50
WIDTH, HEIGHT = 800, 600
GRAVITY = 10
THRUST = 50
FUEL_CONSUMPTION = 1
ROTATION_SPEED = 90
DT = 1 / FPS


MAX_LANDING_SPEED = 10.0


EMPTY_MASS = 1
MASS_PER_FUEL_UNIT = 0.001
INIT_FUEL = 1000
INIT_X = 200
INIT_Y = 100
INIT_X_SPEED = 0
INIT_Y_SPEED = 0
INIT_ANGLE = 0


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)


curr_folder = os.path.dirname(__file__)


# Load images
spaceship_image = pygame.image.load(os.path.join(curr_folder, "images", "spaceship.png"))
spaceship_thrust_image = pygame.image.load(
    os.path.join(curr_folder, "images", "spaceship_thrust.png")
)


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
        self.fuel = INIT_FUEL
        self.thrusting = False
        self.mass = EMPTY_MASS + self.fuel * MASS_PER_FUEL_UNIT

    def update(self, keys):
        self.thrusting = False
        if self.fuel > 0:
            if keys[pygame.K_UP]:
                self.fuel -= FUEL_CONSUMPTION
                self.mass = EMPTY_MASS + self.fuel * MASS_PER_FUEL_UNIT
                thrust_vector = pygame.math.Vector2(0.0, -THRUST).rotate(-self.angle)
                self.velocity += DT * thrust_vector
                self.thrusting = True
            if keys[pygame.K_LEFT]:
                self.angle += DT * ROTATION_SPEED
            if keys[pygame.K_RIGHT]:
                self.angle -= DT * ROTATION_SPEED

        # Apply gravity
        self.velocity.y += DT * GRAVITY

        # Update position
        self.position.x += DT * self.velocity.x
        self.position.y += DT * self.velocity.y

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
        if self.rect.center[1] > HEIGHT + 20:
            self.rect.center[1] = HEIGHT + 20
            self.velocity.y = 0

    def draw(self, screen):
        if self.thrusting:
            screen.blit(self.thrust_image, self.rect.topleft)
        else:
            screen.blit(self.image, self.rect.topleft)


def write_results(fuel, speed, height, success: str):
    with open("results.txt", "a") as f:
        t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(
            f"Time: {t}, Fuel: {fuel:.2f}, Speed: {speed:.2f}, Height: {height:.2f}, {success}\n"
        )


def write_state(spaceship: Spaceship):
    with open(os.path.join(os.path.dirname(__file__), "state.json"), "w") as f:
        t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        state = {
            "time": t,
            "thrust": THRUST,
            "gravity": GRAVITY,
            "empty-mass": EMPTY_MASS,

            "fuel-mass": spaceship.fuel * MASS_PER_FUEL_UNIT,
            "fuel-consumption": FUEL_CONSUMPTION,
            "vertcal-speed": spaceship.velocity.y,
            "horizontal-speed": spaceship.velocity.x,
            "angle": spaceship.angle,
            "vertical-position": spaceship.rect.center[1],
            "horizontal-position": spaceship.rect.center[0],
        }
        json.dump(state, f, indent=4)


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
            if (
                event.type == pygame.QUIT
                or event.type == pygame.KEYDOWN
                and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and not running:
                if event.key == pygame.K_SPACE:
                    spaceship, running, landing_site_x = reset_game()

        speed = math.sqrt(spaceship.velocity.x**2 + spaceship.velocity.y**2)
        height = HEIGHT - spaceship.rect.center[1] - 20

        screen.fill(BLACK)

        if running:
            keys = pygame.key.get_pressed()
            spaceship.update(keys)
            write_state(spaceship)

            # Check for landing or crash
            if height <= 2:
                running = False
                if speed < MAX_LANDING_SPEED:
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

        else:
            screen.blit(
                message,
                (
                    WIDTH // 2 - message.get_width() // 2,
                    HEIGHT // 2 - message.get_height() // 2,
                ),
            )
            retry_message = font.render("Press spacebar to try again", True, WHITE)
            screen.blit(
                retry_message,
                (
                    WIDTH // 2 - retry_message.get_width() // 2,
                    HEIGHT // 2 + message.get_height(),
                ),
            )

        pygame.draw.line(
            screen, WHITE, (0, HEIGHT - 10), (WIDTH, HEIGHT - 10), 5
        )  # Draw the planet surface as a white line
        pygame.draw.line(
            screen,
            RED,
            (landing_site_x, HEIGHT - 10),
            (landing_site_x + 50, HEIGHT - 10),
            5,
        )  # Draw the landing site as a red line
        spaceship.draw(screen)

        # Render fuel text
        fuel_text = font.render(f"Fuel: {int(spaceship.fuel)}", True, WHITE)
        screen.blit(fuel_text, (10, 10))

        # Render speed magnitude text
        speed_text = font.render(
            f"Speed: {speed:.2f}", True, RED if speed > MAX_LANDING_SPEED else WHITE
        )
        screen.blit(speed_text, (10, 40))

        # Render height text
        height_text = font.render(f"Height: {height:.2f}", True, WHITE)
        screen.blit(height_text, (10, 70))

        time_text = font.render(f"Time {pygame.time.get_ticks()/1000:.2f}", True, WHITE)
        screen.blit(time_text, (10, 100))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
