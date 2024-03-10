import pygame
import sys
from add_point_window import create_point

# Initialize Pygame
pygame.init()

# Set the dimensions of the window
screen = pygame.display.set_mode((500, 500))


def create_dot():
    name, x, y = create_point()
    pygame.draw.circle(screen, (0, 255, 0), (x, y), 5)


# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_c:
            create_dot()

    pygame.display.update()
