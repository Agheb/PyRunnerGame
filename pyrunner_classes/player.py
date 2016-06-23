#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This module is used to hold the Player class. The Player represents the user-
controlled sprite on the screen.
Passing sprite_sheet.getimage(x position in pixels upper left corner, y position in pixels upper left corner,
widht of image, height of image) to spritesheet_handling to cut the sprite out of the sprite sheet.
"""
# Python 2 related fixes
from __future__ import division
import pygame
from .spritesheet_handling import SpriteSheet

SPRITE_SHEET_PATH = "./resources/sprites/LRCharacters32.png"


class Player(pygame.sprite.DirtySprite):
    """defines the main player"""

    def __init__(self, pos, tile_size=32, fps=25):
        pygame.sprite.DirtySprite.__init__(self)
        self.tile_size = tile_size
        self.fps = fps
        # positional attributes
        self.on_ground = False
        self.on_ladder = False
        self.on_rope = False
        self.stop_on_ground = False
        # movement related
        self.change_x = 0
        self.change_y = 0
        self.speed = 4
        # score related
        self.gold_count = 0
        # lists holding the image for movement. Up and down movement uses the same sprites.
        self.walking_frames_l = []
        self.walking_frames_r = []
        self.walking_frames_ud = []
        self.digging_frames_l = []
        self.digging_frames_r = []
        self.hanging_frames_l = []
        self.hanging_frames_r = []
        self.sprite_sheet = SpriteSheet(SPRITE_SHEET_PATH, self.tile_size, self.fps)

        # Load all the left facing images into a list (x, y, height, width)
        self.sprite_sheet.add_animation(0, 0, self.walking_frames_l, 4)
        # Load all the left facing images into a list and flip them to make them face right
        self.sprite_sheet.add_animation(0, 0, self.walking_frames_r, 4, True)
        # Load all the up / down facing images into a list
        self.sprite_sheet.add_animation(0, 1, self.walking_frames_ud, 4)
        # Load all the digging left images
        self.sprite_sheet.add_animation(0, 2, self.digging_frames_l, 3)
        # Load all the digging left images and flip them do digging right
        self.sprite_sheet.add_animation(0, 2, self.digging_frames_r, 3, True)
        # Load the left hanging images into a list
        self.sprite_sheet.add_animation(4, 1, self.hanging_frames_l, 4)
        # Load the left hanging images into a list and flip them to face right
        self.sprite_sheet.add_animation(4, 1, self.hanging_frames_r, 4, True)

        # Stop Frame: Sprite when player is not moving on ground
        self.stop_frame = self.sprite_sheet.add_animation(5, 0)

        self.direction = "Stop"  # direction the player is facing at the beginning of the game

        # Set the image the player starts with
        self.image = self.stop_frame
        # Set a reference to the image rect.
        self.rect = self.image.get_rect()

        self.rect.x, self.rect.y = pos

    # Player-controlled movement:
    def go_left(self):
        """" Called when the user hits the left arrow. Checks if player is on Rope to change animation """
        if self.on_ground or self.on_rope:
            self.change_x = -self.speed
        else:
            self.change_x = 0

        if self.on_rope:
            self.direction = "RL"
        else:
            self.direction = "L"

    def go_right(self):
        """ Called when the user hits the right arrow. Checks if player is on Rope to change animation """
        if self.on_ground or self.on_rope:
            self.change_x = self.speed

        if self.on_rope:
            self.direction = "RR"
        else:
            self.direction = "R"

    def go_up(self):
        """ Called when the user hits the up arrow. Only Possible when Player is on a ladder"""
        if self.on_ladder:
            self.change_y = -self.speed
            self.direction = "UD"

    def go_down(self):
        """ Called when the user hits the down arrow. Only Possible when Player is on a ladder"""
        if self.on_ladder:
            self.change_y = self.speed
            self.direction = "UD"
        elif self.on_rope:
            self.change_y = self.speed
            self.rect.y += self.speed + self.speed
            self.direction = "UD"
            self.on_rope = False

    def schedule_stop(self):
        """stop player movements"""
        self.stop_on_ground = True

    def dig_right(self):
        """dig to the right"""
        if self.on_ladder or self.on_rope:
            pass
        else:
            self.direction = "DR"
            print("digging right")
            # self.player_collide()

    def dig_left(self):
        """dig to the left"""
        if self.on_ladder or self.on_rope:
            pass
        else:
            self.direction = "DL"
            print("digging left")
            # self.player_collide()

    def update(self):  # updates the images and creates motion with sprites
        """ Move the player. """
        self.dirty = 1

        # Move left/right
        self.rect.x += self.change_x
        self.rect.y += self.change_y

        # Animations with Sprites
        pos_x = self.rect.x
        pos_y = self.rect.y

        '''movements'''
        if self.direction == "R":
            self.image = self.sprite_sheet.get_frame(pos_x, self.walking_frames_r)
        elif self.direction == "L":
            self.image = self.sprite_sheet.get_frame(pos_x, self.walking_frames_l)
        elif self.direction == "UD":
            self.sprite_sheet.get_frame(pos_y, self.walking_frames_ud)
        elif self.direction == "RR":
            self.sprite_sheet.get_frame(pos_x, self.hanging_frames_r)
        elif self.direction == "RL":
            self.sprite_sheet.get_frame(pos_x, self.walking_frames_l)
        elif self.direction == "Stop":
            self.image = self.stop_frame
        elif self.direction == "DL":
            # Dig left/right
            self.image = self.digging_frames_l[0]
            self.image = self.digging_frames_l[1]
            self.image = self.digging_frames_l[2]
        elif self.direction == "DR":
            self.image = self.digging_frames_r[0]
            self.image = self.digging_frames_r[1]
            self.image = self.digging_frames_r[2]

        # Gravity
        self.calc_gravity()

    def calc_gravity(self):
        """ Calculate effect of gravity. """
        # See if we are on the ground and not on a ladder or rope
        if not self.on_ground and not self.on_ladder and not self.on_rope:
                self.change_y += .35

        if self.stop_on_ground:
            if self.rect.y % self.tile_size is not 0:
                if self.change_y < 0:
                    self.go_up()
                else:
                    self.go_down()
            else:
                self.change_y = 0

            if self.rect.x % self.tile_size is not 0:
                if self.change_x > 0:
                    self.go_right()
                else:
                    self.go_left()
            else:
                self.change_x = 0

            if self.change_x is 0 and self.change_y is 0:
                self.stop_on_ground = False
                self.direction = "Stop"
