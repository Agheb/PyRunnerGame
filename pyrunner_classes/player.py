#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This module is used to hold the Player/Bot class. The Player represents the user-
controlled sprite on the screen. Bots are controlled by the computer inheriting from Player in the non_player_characters
through the state_machine, npc_states.
Passing sprite_sheet.getimage(x position in pixels upper left corner, y position in pixels upper left corner,
widht of image, height of image) to spritesheet_handling to cut the sprite out of the sprite sheet.
"""
# Python 2 related fixes
from __future__ import division
import pygame
from .spritesheet_handling import SpriteSheet
from .player_objects import GoldScore


class Player(pygame.sprite.DirtySprite):
    """defines the main  player and bots"""

    group = pygame.sprite.LayeredDirty(default_layer=1)

    def __init__(self, pos, sheet, pid=1, tile_size=32, level=None, fps=25, bot=False):
        pygame.sprite.DirtySprite.__init__(self, Player.group)
        self.pid = pid
        self.tile_size = tile_size
        self.level = level
        self.pixel_diff = self.level.pixel_diff if self.level else 0
        self.size = self.tile_size + self.pixel_diff
        self.fps = fps
        self.is_human = True if not bot else False
        # positional attributes
        self.x, self.y = pos
        self.on_tile = None
        self.on_ground = False
        self.on_ladder = False
        self.on_rope = False
        self.can_jump_off = False
        self.can_go_down = False
        self._stop_on_ground = False
        # movement related
        self.change_x = 0
        self.change_y = 0
        self.speed = self.size // 10 * 2
        # lists holding the image for movement. Up and down movement uses the same sprites.
        self.spawn_frames = []
        self.walking_frames_l = []
        self.walking_frames_r = []
        self.walking_frames_ud = []
        self.falling_frames = []
        self.hanging_frames_l = []
        self.hanging_frames_r = []
        self.death_frames = []
        self.sprite_sheet = SpriteSheet(sheet, self.tile_size, self.pixel_diff, self.fps)
        # animation relevant values
        self.spawning = True
        self.spawn_frame = 0
        self.killed = False
        self.killed_frame = 0
        self.digging_frame = 0
        self.robbed_gold = None
        # position to aim for
        self.stop_at_x = 0
        self.stop_at_y = 0
        self.is_human = False if bot else True
        self.reached_exit = False

        if self.is_human:
            # score related
            self.score_left = True if not self.pid % 2 else False
            self.score_up = True if self.pid <= 2 else False
            # check for existing scores
            existing_score = None
            for score in GoldScore.scores:
                if not score.child_num and score.gid is self.pid:
                    existing_score = score
                    break
            if existing_score:
                self.gold_score = existing_score
                self.gold_score.change_player(self)
            else:
                self.gold_score = GoldScore(self)
            # animations
            self.digging_frames_l = []
            self.digging_frames_r = []

            # Load all frames for the spawn animation
            self.spawn_frames = self.sprite_sheet.add_animation(8, 1, 4)
            # Load all the left facing images into a list (x, y, height, width)
            self.walking_frames_l = self.sprite_sheet.add_animation(0, 0, 4)
            # Load all the left facing images into a list and flip them to make them face right
            self.walking_frames_r = self.sprite_sheet.flip_frames(self.walking_frames_l)
            # Load all the up / down facing images into a list
            self.walking_frames_ud = self.sprite_sheet.add_animation(0, 1, 4)
            # Load all falling down frames
            self.falling_frames = self.sprite_sheet.add_animation(4, 0, 4)
            # Load all the digging left images
            self.digging_frames_l = self.sprite_sheet.add_animation(0, 2, 3)
            # Load all the digging left images and flip them do digging right
            self.digging_frames_r = self.sprite_sheet.flip_frames(self.digging_frames_l)
            # Load the left hanging images into a list
            self.hanging_frames_l = self.sprite_sheet.add_animation(4, 1, 4)
            # Load the left hanging images into a list and flip them to face right
            self.hanging_frames_r = self.sprite_sheet.flip_frames(self.hanging_frames_l)
            # death animation
            self.death_frames = self.sprite_sheet.add_animation(5, 2, 8)
            # Stop Frame: Sprite when player is not moving on ground
            self.stand_left = self.sprite_sheet.add_animation(2, 2)
            self.stand_right = self.sprite_sheet.add_animation(3, 2)
            self.trapped = self.sprite_sheet.add_animation(5, 0)

            self.direction = "Stop"  # direction the player is facing at the beginning of the game
            # Set the image the player starts with
            self.image = self.stand_right
            # Set a reference to the image rect.
            self.rect = self.image.get_rect()
            # spawn the player at the desired location
            self.rect.topleft = pos

    # Player-controlled movement:
    def go_left(self):
        """" Called when the user hits the left arrow. Checks if player is on Rope to change animation """
        if self.direction is not "Trapped" and self.change_y is 0:
            self.change_x = -self.speed if self.change_y <= self.speed else 0

            if self.on_rope:
                self.direction = "RL"
            elif self.on_ladder and not self.on_ground:
                self.direction = "UD"
            else:
                self.direction = "L"

    def go_right(self):
        """ Called when the user hits the right arrow. Checks if player is on Rope to change animation """
        if self.direction is not "Trapped" and self.change_y is 0:
            self.change_x = self.speed if self.change_y <= self.speed else 0

            if self.on_rope:
                self.direction = "RR"
            elif not self.on_ground and self.on_ladder:
                self.direction = "UD"
            else:
                self.direction = "R"

    def go_up(self):
        """ Called when the user hits the up arrow. Only Possible when Player is on a ladder"""
        if self.on_ladder and self.change_x is 0:
            self.change_y = -self.speed
            self.direction = "UD"

    def go_down(self):
        """ Called when the user hits the down arrow. Only Possible when Player is on a ladder"""
        if self.direction is not "Trapped":
            if self.on_rope:
                '''only let the player jump down if there's no bottom tile below'''
                if self.can_jump_off:
                    self.rect.y += self.speed * 2
                    self.on_rope = False
                    self.on_ladder = False
                    self.on_ground = False
            elif self.change_y < self.speed:
                '''don't let the player slow down while falling by pressing the down key again'''
                self.direction = "UD"
                self.rect.y += self.speed
                self.change_y = self.speed

    @property
    def stop_on_ground(self):
        """get if the player is scheduled to stop on the next tile"""
        return self._stop_on_ground

    @stop_on_ground.setter
    def stop_on_ground(self, value):
        """stop player movements"""
        if value:
            if self.change_y <= self.speed:
                '''make sure the player is not falling down'''
                self._stop_on_ground = value
        else:
            self._stop_on_ground = value
            self.stop_at_x = 0
            self.stop_at_y = 0

    def dig_right(self):
        """dig to the right"""
        if self.on_ground and self.direction is not "Trapped":
            self.stop_on_ground = True
            self.direction = "DR"
            # self.player_collide()

    def dig_left(self):
        """dig to the left"""
        if self.on_ground and self.direction is not "Trapped":
            self.stop_on_ground = True
            self.direction = "DL"
            # self.player_collide()

    def process(self):
        """needed for the bots"""
        pass

    def update(self):  # updates the images and creates motion with sprites
        """ Move the player. """
        self.dirty = 1

        if not self.is_human:
            self.process()

        if self.spawning:
            self.image = self.spawn_frames[self.spawn_frame]
            self.spawn_frame += 1

            if self.spawn_frame is len(self.spawn_frames):
                self.spawning = False
                self.image = self.stand_right
        elif not self.killed:
            # Move left/right
            self.rect.x += self.change_x
            self.rect.y += self.change_y
            self.x, self.y = self.rect.topleft

            '''keep the correct movement animation according to the direction on screen'''
            if self.change_x < 0:
                self.direction = "RL" if self.on_rope else "L"
            elif self.change_x > 0:
                self.direction = "RR" if self.on_rope else "R"
            elif not self.on_ground and not self.on_rope and not self.on_ladder and self.speed < self.change_y:
                self.direction = "Falling"

            # Animations with Sprites
            '''movements'''
            if self.direction == "R":
                self.image = self.sprite_sheet.get_frame(self.x, self.walking_frames_r)
            elif self.direction == "L":
                self.image = self.sprite_sheet.get_frame(self.x, self.walking_frames_l)
            elif self.direction == "UD":
                self.image = self.sprite_sheet.get_frame(self.y, self.walking_frames_ud)
            elif self.direction == "Falling":
                self.image = self.sprite_sheet.get_frame(self.y, self.falling_frames, 2)
            elif self.direction == "RR":
                self.image = self.sprite_sheet.get_frame(self.x, self.hanging_frames_r)
            elif self.direction == "RL":
                self.image = self.sprite_sheet.get_frame(self.x, self.hanging_frames_l)
            elif self.direction == "SR":
                self.image = self.stand_right
            elif self.direction == "SL":
                self.image = self.stand_left
            elif self.direction == "Stop":
                # self.image = self.stand_right
                pass
            elif self.direction == "Trapped":
                self.image = self.trapped
            elif self.direction == "DL":
                # Dig left/right
                self.image = self.digging_frames_l[self.digging_frame // 4]
                self.digging_frame += 1
                if self.digging_frame is len(self.digging_frames_l) * 4:
                    self.digging_frame = 0
                    self.direction = "Stop"
            elif self.direction == "DR":
                self.image = self.digging_frames_r[self.digging_frame // 4]
                self.digging_frame += 1
                if self.digging_frame is len(self.digging_frames_l) * 4:
                    self.digging_frame = 0
                    self.direction = "Stop"

            # Gravity
            self.calc_gravity()
        else:
            self.image = self.death_frames[self.killed_frame // 2]
            self.killed_frame += 1

            if self.killed_frame is len(self.death_frames) * 2:
                if not self.is_human and self.robbed_gold:
                    '''restore robbed gold'''
                    self.robbed_gold.rect.bottomleft = self.rect.topleft
                    self.robbed_gold.dirty = 1
                pygame.sprite.DirtySprite.kill(self)


    def calc_gravity(self):
        """ Calculate effect of gravity. """
        # See if we are on the ground and not on a ladder or rope
        if not self.on_ground and not self.on_ladder and not self.on_rope and self.direction is not "Trapped":
            if self.speed <= self.change_y <= self.speed * 2.5:
                self.change_y += .35
            else:
                self.change_y = self.speed

        if self.stop_on_ground:
            if self.change_x is not 0:
                if self.reached_next_tile(self.change_x):
                    if self.rect.x - self.size <= self.stop_at_x <= self.rect.x + self.size:
                        '''make sure the player won't get set to a too far away location'''
                        self.rect.x = self.stop_at_x
                    self.stop_at_x = 0
                    if not self.on_rope:
                        if self.change_x > 0:
                            self.direction = "SR"
                        else:
                            self.direction = "SL"
                    self.change_x = 0
                else:
                    if self.change_x > 0:
                        self.go_right()
                    else:
                        self.go_left()

            if self.change_y is not 0:
                if self.change_y <= self.speed and self.direction is not "Falling":
                    if self.reached_next_tile(self.change_y):
                        if self.rect.y - self.size <= self.stop_at_y <= self.rect.y + self.size:
                            '''make sure the player won't get set to a too far away location'''
                            self.rect.y = self.stop_at_y
                        self.stop_at_y = 0
                        self.change_y = 0
                    else:
                        if self.change_y < 0:
                            self.go_up()
                        else:
                            self.go_down()

            if self.change_x is 0 and self.change_y is 0:
                self.stop_on_ground = False

    def set_stop_point(self, speed):
        """set the coordinates where the player should stop"""
        x, y = self.rect.topleft

        if speed is self.change_x and self.stop_at_x is 0:
            diff = self.size - (x % self.size)
            x += diff if speed > 0 else -diff
            self.stop_at_x = x
            self.stop_at_y = 0
        elif speed is self.change_y and self.stop_at_y is 0:
            diff = self.size - (y % self.size)
            y += diff if speed > 0 else -diff
            self.stop_at_x = 0
            self.stop_at_y = y

    def reached_next_tile(self, speed):
        """stop the player in a certain direction"""
        stopped = False
        pos_x, pos_y = self.rect.topleft

        self.set_stop_point(speed)

        x, y = self.stop_at_x, self.stop_at_y

        if speed is self.change_x and speed > 0 and pos_x >= x:
            stopped = True
        elif speed is self.change_x and speed < 0 and pos_x <= x:
            stopped = True
        elif speed is self.change_y and speed > 0 and pos_y >= y:
            stopped = True
        elif speed is self.change_y and speed < 0 and pos_y <= y:
            stopped = True

        return stopped

    def kill(self):
        """kill animation"""
        if self.is_human and not self.reached_exit:
            '''if the player dies in the level remove his gold'''
            self.gold = 0
            self.gold_score.kill()
        self.killed = True

    @property
    def gold(self):
        """returns the players gold"""
        return self.gold_score.gold

    @gold.setter
    def gold(self, amount):
        """set the gold value of this player to amount"""
        self.gold_score.gold = amount

    def add_gold(self):
        """increase the gold count by 1"""
        self.gold_score.gold += 1

    def get_location(self):
        return self.rect.center
