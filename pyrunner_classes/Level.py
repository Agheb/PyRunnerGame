import pygame

background_colour = (255,255,255)
(width, height) = (300, 200)

BLACK = (0, 0, 0)


class Particle:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.colour = (0, 0, 255)
        self.thickness = 1
        self.position = (x, y)

    def display(self):
        pygame.draw.circle(screen, BLACK, (140, 120), 20, 0)
        pygame.draw.circle(screen, BLACK, (100, 20), 20, 0)
        pygame.draw.circle(screen, BLACK, (50, 22), 20, 0)
        pygame.draw.circle(screen, BLACK, (200, 100), 20, 0)

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Tutorial 2')
screen.fill(background_colour)

my_first_particle = Particle(150, 50, 15)
my_first_particle.display()

pygame.display.flip()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
