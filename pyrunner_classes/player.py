"""
This module is used to hold the Player class. The Player represents the user-
controlled sprite on the screen.
Passing sprite_sheet.getimage(x position in pixels upper left corner, y position in pixels upper left corner,
widht of image, height of image) to spritesheet_handling to cut the sprite out of the sprite sheet.
"""
import pygame
from .spritesheet_handling import SpriteSheet

SPRITE_SHEET_PATH = "./resources/sprites/LRCharacters32.png"


class Player(pygame.sprite.DirtySprite):
    """defines the main player"""

    def __init__(self):
        super().__init__()

        self.on_ground = False
        self.on_ladder = False
        self.on_rope = True
        self.stop_on_ground = False
        self.change_x = 0
        self.change_y = 0

        self.boundary_top = 0
        self.boundary_bottom = 0
        self.boundary_left = 0
        self.boundary_right = 0

        self.gold_count = 0

        self.level = None
        self.player = None

        # list holding the image for movement. Up and down movement uses the same sprites.
        self.walking_frames_l = []
        self.walking_frames_r = []
        self.walking_frames_ud = []
        self.digging_frames_l = []
        self.digging_frames_r = []
        self.hanging_frames_l = []
        self.hanging_frames_r = []

        sprite_sheet = SpriteSheet(SPRITE_SHEET_PATH)

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
        image = sprite_sheet.get_image(64, 64, 32, 32)
        self.digging_frames_l.append(image)
        image = sprite_sheet.get_image(32, 64, 32, 32)
        self.digging_frames_l.append(image)
        image = sprite_sheet.get_image(0, 64, 32, 32)
        self.digging_frames_l.append(image)

        # Load all the digging left images and flip them do digging right
        image = sprite_sheet.get_image(64, 64, 32, 32)
        image = pygame.transform.flip(image, True, False)
        self.digging_frames_r.append(image)
        image = sprite_sheet.get_image(32, 64, 32, 32)
        image = pygame.transform.flip(image, True, False)
        self.digging_frames_r.append(image)
        image = sprite_sheet.get_image(0, 64, 32, 32)
        image = pygame.transform.flip(image, True, False)
        self.digging_frames_r.append(image)

        # Load the left hanging images into a list
        image = sprite_sheet.get_image(128, 32, 32, 32)
        self.hanging_frames_l.append(image)
        image = sprite_sheet.get_image(160, 32, 32, 32)
        self.hanging_frames_l.append(image)
        image = sprite_sheet.get_image(192, 32, 32, 32)
        self.hanging_frames_l.append(image)
        image = sprite_sheet.get_image(224, 32, 32, 32)
        self.hanging_frames_l.append(image)

        # Load the left hanging images into a list and flip them to right
        image = sprite_sheet.get_image(128, 32, 32, 32)
        image = pygame.transform.flip(image, True, False)
        self.hanging_frames_l.append(image)
        image = sprite_sheet.get_image(160, 32, 32, 32)
        image = pygame.transform.flip(image, True, False)
        self.hanging_frames_l.append(image)
        image = sprite_sheet.get_image(192, 32, 32, 32)
        image = pygame.transform.flip(image, True, False)
        self.hanging_frames_l.append(image)
        image = sprite_sheet.get_image(224, 32, 32, 32)
        image = pygame.transform.flip(image, True, False)
        self.hanging_frames_l.append(image)

        # Stop Frame
        self.stop_frame = sprite_sheet.get_image(160, 0, 32, 32)

        self.direction = "Stop"  # direction the player is facing at the beginning of the game

        # Set the image the player starts with
        self.image = self.walking_frames_r[0]
        # Set a reference to the image rect.
        self.rect = self.image.get_rect()

    # Player-controlled movement:
    def go_left(self):
        """" Called when the user hits the left arrow. Checks if player is on Rope to change animation """
        self.change_x = -5
        if self.on_rope:
            self.direction = "RL"
        else:
            self.direction = "L"

    def go_right(self):
        """ Called when the user hits the right arrow. Checks if player is on Rope to change animation """
        self.change_x = 5
        if self.on_rope:
            self.direction = "RR"
            print(self.direction, self.on_rope)
        else:
            self.direction = "R"

    def go_up(self):
        """ Called when the user hits the up arrow. Only Possible when Player is on a ladder"""
        if self.on_ladder:
            self.change_y = -5
            self.direction = 'UD'
        else:
            pass

    def go_down(self):
        """ Called when the user hits the down arrow. Only Possible when Player is on a ladder"""
        if self.on_ladder:
            self.change_y = 5
            self.direction = 'UD'
        else:
            pass

    def schedule_stop(self):
        self.stop_on_ground = True
        self.direction = "Stop"

    def dig_right(self):
        self.direction = "DR"
        print("digging right")
        self.player_collide()

    def dig_left(self):
        self.direction = "DL"
        print("digging left")
        self.player_collide()

    def update(self):  # updates the images and creates motion with sprites
        """ Move the player. """
        # Gravity
        self.calc_grav()
        self.dirty = 1

        # Move left/right
        self.rect.x += self.change_x
        self.rect.y += self.change_y

        # Animations with Sprites
        posx = self.rect.x
        posy = self.rect.y
        if self.direction == "R":
            frame = (posx // 30) % len(self.walking_frames_r)
            self.image = self.walking_frames_r[frame]
        elif self.direction == "L":
            frame = (posx // 30) % len(self.walking_frames_l)
            self.image = self.walking_frames_l[frame]

        # Move up/down uses the same sprites
        if self.direction == "UD":
            frame = (posy // 30) % len(self.walking_frames_ud)
            self.image = self.walking_frames_ud[frame]

        # Dig left/right
        if self.direction == "DL":
            self.image = self.digging_frames_l[0]
            self.image = self.digging_frames_l[1]
            self.image = self.digging_frames_l[2]
        elif self.direction == "DR":
            self.image = self.digging_frames_r[0]
            self.image = self.digging_frames_r[1]
            self.image = self.digging_frames_r[2]

        # Hang left/right
        if self.direction == "RR":
            frame = (posx // 30) % len(self.hanging_frames_r)
            self.image = self.hanging_frames_r[frame]
        elif self.direction == "RL":
            frame = (posx // 30) % len(self.hanging_frames_l)
            self.image = self.hanging_frames_l[frame]

        # stop frame
        if self.direction == "Stop":
            self.image = self.stop_frame

    def calc_grav(self):
        """ Calculate effect of gravity. """

        # See if we are on the ground and not on a ladder or rope
        if not self.on_ground and (not self.on_ladder or not self.on_rope):
            self.change_y += .35

        if self.stop_on_ground and self.on_ground:
            self.change_y = 0
            self.change_x = 0
            self.stop_on_ground = False

    def player_collide(self):
        col_list = pygame.sprite.collide_rect_ratio(1.5)
        print(col_list)
        return col_list
