import pygame
import constants
import platforms


class Level:
    """ This is a generic super-class used to define a level.
        Create a child class for each level with level-specific
        info. """

    def __init__(self):

        # Lists of sprites used in all levels.
        self.platform_list = None
        self.enemy_list = None

        self.platform_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()

    # Update everything on this level
    def update(self):
        """ Update everything in this level."""
        self.platform_list.update()
        self.enemy_list.update()

    def draw(self, screen):
        """ Draw everything on this level."""
        # Draw all the sprite lists that we have
        self.platform_list.draw(screen)
        # self.enemy_list.draw(screen)


# Create platforms for the level
class LevelOne(Level):
    """ Definition for level 1. """

    def __init__(self):
        """ Create level 1. """

        # Call the parent constructor
        Level.__init__(self)

        # Array with type of platform, and x, y location of the platform.
        level = [[platforms.BRICKWALL, 400, 0],
                 [platforms.WALL, 200, 0]]

        # Go through the array above and add platforms
        for platform in level:
            block = platforms.Platform(platform[0])
            block.rect.x = platform[1]
            block.rect.y = platform[2]
            # block.player = self.player
            self.platform_list.add(block)
