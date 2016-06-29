#!/usr/bin/python
# -*- coding: utf-8 -*-
"""main pyRunner class which initializes all sub classes and threads"""
# Python 2 related fixes
from __future__ import division
import pygame
from .spritesheet_handling import SpriteSheet


class GoldScore(pygame.sprite.DirtySprite):
    """store and show the gold of each player"""

    scores = pygame.sprite.LayeredDirty(default_layer=1)

    def __init__(self, player):
        pygame.sprite.DirtySprite.__init__(self, GoldScore.scores)
        self.player = player
        self.level = self.player.level
        self.pixel_diff = self.player.pixel_diff
        self.fps = self.player.fps
        self._gold = 0
        self.tile_size = 32
        self.min_pixels = 6
        self.sprite_sheet = SpriteSheet("gold.png", self.tile_size, self.pixel_diff - self.min_pixels, self.fps, False)
        self.gold_rotation = self.sprite_sheet.add_animation(0, 0, 8)
        self.image = self.gold_rotation[0]
        self.rect = self.image.get_rect()
        self.rect.topleft = (0, 0)
        self.rect.x += self.level.margin_left
        self.rect.y += self.level.margin_top
        self.left = self.player.score_left
        self.up = self.player.score_up
        self.frame_counter = 0
        self.fps = self.player.fps
        self.fps_counter = 0
        self.children = []
        self.changed = True
        x, y = self.rect.topleft
        diff = self.tile_size + self.pixel_diff
        if not self.left:
            x += self.level.width - diff
            self.rect.x = x + self.min_pixels
        if not self.up:
            y += self.level.height - diff
            self.rect.y = y + self.min_pixels
        self.pos = x, y
        print(str(self.pos))
        print(str(self.rect))

        '''the coin is smaller than 32 pixels so we render it centered in a 32x32 tile'''
        self.rect.x += 3 if self.left else -3
        self.rect.y += 3 if self.up else -3

    def update(self):
        """show rotating gold coin"""
        if self.frame_counter < len(self.gold_rotation):
            # count the frames
            if self.fps_counter is self.fps:
                self.fps_counter = 0
            else:
                self.fps_counter += 1

            # only change animation every second frame
            if self.fps_counter & 1:
                self.image = self.gold_rotation[self.frame_counter]
                self.frame_counter += 1
        else:
            '''update gold counter only once per second'''
            self.frame_counter = 0

            if self.changed:
                self.changed = False
                '''convert the number to single numbers in a list'''
                num = [int(i) for i in str(self.gold)]
                length = len(num)
                children = len(self.children)

                if children < length:
                    '''if the number is greater then our current sprites we need to add another one'''
                    self.children.append(ScoreNumber(self, 0, children + 1))
                elif children > length:
                    '''if there's more numbers then we need we can remove the last one (at a time)'''
                    self.children.pop().kill()

                for i, child in enumerate(self.children):
                    '''the number on the right side are in reverse order'''
                    pos = i if self.left else length - i - 1
                    child.set_number(num[pos])

        # this frame should be rendered permanently
        self.dirty = 1

    @property
    def gold(self):
        """the amount of gold this object stores"""
        return self._gold

    @gold.setter
    def gold(self, amount):
        if self._gold is not amount:
            self._gold = amount
            self.changed = True

    def kill(self):
        """do a homicide to your family"""
        for child in self.children:
            child.kill()

        pygame.sprite.DirtySprite.kill(self)


class ScoreNumber(pygame.sprite.DirtySprite):
    """show the current amount of gold a player has collected"""

    def __init__(self, gold_score, number=0, child_num=1):
        pygame.sprite.DirtySprite.__init__(self, GoldScore.scores)
        self.gs = gold_score
        self.pos = self.gs.pos
        self.pixel_diff = self.gs.pixel_diff
        self.fps = self.gs.fps
        self.sprite_sheet = SpriteSheet("numbers_gold_320x32.png", 32, self.pixel_diff, self.fps, False)
        self.number = number
        self.numbers = self.sprite_sheet.add_animation(0, 0, 10)
        self.changed = True
        self.image = self.numbers[self.number]
        self.rect = self.image.get_rect()
        self.rect.topleft = self.gs.pos
        self.left = self.gs.left
        self.child_num = child_num
        self.background = self.gs.level.surface
        self.background_clean = None
        '''move the number to the correct position'''
        width = self.image.get_width()
        width *= self.child_num
        self.rect.x += width if self.left else -width
        '''store the current position'''
        self.pos = self.rect.topleft
        self.size = self.image.get_size()
        '''copy a clean version of the background for dirty rect animation'''
        print(str(self.pos))
        self.set_clean_rect()

    def set_number(self, number):
        """set the number to a certain value"""
        if number is not self.number:
            self.number = number
            self.changed = True

    def set_clean_rect(self):
        """copy a clean background once"""
        if self.background:
            try:
                x, y = self.pos
                w, h = self.size
                surface = self.background.copy()
                self.background_clean = surface.subsurface((x, y, w, h))
            except ValueError:
                self.background_clean = None
                print("%(x)s/%(y)s with the dimensions %(w)s/%(h)s is outside of the surface %(surface)s" % locals())

    def draw_clean_background(self):
        """clear the background of the sprite"""
        self.background.blit(self.background_clean, self.pos)

    def update(self):
        """show number"""
        if self.changed:
            if self.number < 10:
                self.image = self.numbers[self.number]

            self.changed = False

            if self.background_clean:
                '''blit the score directly to the level surface so it won't have to refresh each frame'''
                self.draw_clean_background()
                self.background.blit(self.image, self.pos)

        if not self.background:
            '''
                this frame should be rendered permanently
                if it's not blitted to the background with a dirty rect
            '''
            self.dirty = 1

    def kill(self):
        """remove all traces"""
        if self.background_clean:
            self.draw_clean_background()

        pygame.sprite.DirtySprite.kill(self)
