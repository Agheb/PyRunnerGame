"""
This module is used to hold the Player class. The Player represents the user-
controlled sprite on the screen.
"""
import pygame
from .constants import *

from spritesheet_handling import SpriteSheet


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.change_x = 0
        self.change_y = 0

        self.boundary_top = 0
        self.boundary_bottom = 0
        self.boundary_left = 0
        self.boundary_right = 0

        self.level = None
        self.player = None
        # TODO check if player is on a ladder or rope so he can walk up / down
        # self.contactwith = None  # tells the player sprite which blocks he is in contact with

        # list holding the image for movement. Up and down movement uses the same sprites.
        self.walking_frames_l = []
        self.walking_frames_r = []
        self.walking_frames_ud = []
        self.digging_frames_l = []
        self.digging_frames_r = []

        sprite_sheet = SpriteSheet("LRCharacters32.png")

        # Load all the left facing images into a list (x, y, height, width)
        image = sprite_sheet.get_image(96, 0, 32, 32)
        self.walking_frames_l.append(image)
        image = sprite_sheet.get_image(64, 0, 32, 32)
        self.walking_frames_l.append(image)
        image = sprite_sheet.get_image(32, 0, 32, 32)
        self.walking_frames_l.append(image)
        image = sprite_sheet.get_image(0, 0, 32, 32)
        self.walking_frames_l.append(image)

        # Load all the left facing images into a list and flip them to make them face right
        image = sprite_sheet.get_image(96, 0, 32, 32)
        image = pygame.transform.flip(image, True, False)
        self.walking_frames_r.append(image)
        image = sprite_sheet.get_image(64, 0, 32, 32)
        image = pygame.transform.flip(image, True, False)
        self.walking_frames_r.append(image)
        image = sprite_sheet.get_image(32, 0, 32, 32)
        image = pygame.transform.flip(image, True, False)
        self.walking_frames_r.append(image)
        image = sprite_sheet.get_image(0, 0, 32, 32)
        image = pygame.transform.flip(image, True, False)
        self.walking_frames_r.append(image)

        # Load all the up / down facing images into a list
        image = sprite_sheet.get_image(96, 32, 32, 32)
        self.walking_frames_ud.append(image)
        image = sprite_sheet.get_image(64, 32, 32, 32)
        self.walking_frames_ud.append(image)
        image = sprite_sheet.get_image(32, 32, 32, 32)
        self.walking_frames_ud.append(image)
        image = sprite_sheet.get_image(0, 32, 32, 32)
        self.walking_frames_ud.append(image)

        # Load all the digging left images
        image = sprite_sheet.get_image(0, 64, 32, 32)
        self.digging_frames_l.append(image)
        image = sprite_sheet.get_image(16, 64, 32, 32)
        self.digging_frames_l.append(image)

        # Load all the digging left images and flip them do digging right
        image = sprite_sheet.get_image(0, 64, 32, 32)
        image = pygame.transform.flip(image, True, False)
        self.digging_frames_r.append(image)
        image = sprite_sheet.get_image(16, 64, 32, 32)
        image = pygame.transform.flip(image, True, False)
        self.digging_frames_r.append(image)

        # Stop Frame
        self.stop_frame = sprite_sheet.get_image(160, 0, 32, 32)

        self.direction = "R"  # direction the player is facing

        # Set the image the player starts with
        self.image = self.walking_frames_r[0]
        # Set a reference to the image rect.
        self.rect = self.image.get_rect()

    # Player-controlled movement:
    def go_left(self):
        """ Called when the user hits the left arrow. """
        self.change_x = -2
        self.direction = "L"

    def go_right(self):
        """ Called when the user hits the right arrow. """
        self.change_x = 2
        self.direction = "R"

    def go_up(self):

        """ Called when the user hits the up arrow. """
        self.change_y = -2
        self.direction = 'UD'

    def go_down(self):
        """ Called when the user hits the down arrow. """
        self.change_y = 2
        self.direction = 'UD'

    def stop(self):
        """ Called when the user lets off the keyboard. """
        self.change_x = 0
        self.change_y = 0
        self.direction = "Stop"

    def dig_right(self):
        if self.change_y == 0 and self.change_x == 0:
            self.direction = "DR"

    def dig_left(self):
        if self.change_y == 0 and self.change_x == 0:
            self.direction = "DL"

    def update(self):  # updates the frames to create motion with sprites
        """ Move the player. """
        # Gravity
        self.calc_grav()

        # Move left/right
        self.rect.x += self.change_x
        posx = self.rect.x
        if self.direction == "R":
            frame = (posx // 30) % len(self.walking_frames_r)
            self.image = self.walking_frames_r[frame]
        else:
            frame = (posx // 30) % len(self.walking_frames_l)
            self.image = self.walking_frames_l[frame]

        # Move up/down uses the same sprites
        self.rect.y += self.change_y
        posy = self.rect.y
        if self.direction == "UD":
            frame = (posy // 30) % len(self.walking_frames_ud)
            self.image = self.walking_frames_ud[frame]

        # Dig left/right
        if self.direction == "DL":
            self.image = self.digging_frames_l[0]
            # self.image = self.digging_frames_l[1]
        elif self.direction == "DR":
            self.image = self.digging_frames_r[0]
            # self.image = self.digging_frames_r[1]

        if self.direction == "Stop":
            self.image = self.stop_frame

    def calc_grav(self):
        """ Calculate effect of gravity. """
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += .35

        # See if we are on the ground.
        if self.rect.y >= constants.SCREEN_HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = constants.SCREEN_HEIGHT - self.rect.height
