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

    def __init__(self, player, pos, left=True, background=None):
        pygame.sprite.DirtySprite.__init__(self, GoldScore.scores)
        self.player = player
        self.pixel_diff = self.player.pixel_diff
        self.fps = self.player.fps
        self.pos = pos
        self.gold = 0
        self.sprite_sheet = SpriteSheet("gold.png", 32, self.pixel_diff - 6, self.fps, False)
        self.gold_rotation = self.sprite_sheet.add_animation(0, 0, 8)
        self.image = self.gold_rotation[0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.rect.x += 3
        self.rect.y += 3
        self.left = left
        self.frame_counter = 0
        self.fps = self.player.fps
        self.fps_counter = 0
        self.children = []

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
            if self.player.gold_count is not self.gold:
                self.gold = self.player.gold_count
            self.frame_counter = 0

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


class ScoreNumber(pygame.sprite.DirtySprite):
    """show the current amount of gold a player has collected"""

    def __init__(self, gold_score, number=0, child_num=1):
        pygame.sprite.DirtySprite.__init__(self, GoldScore.scores)
        self.gs = gold_score
        self.pixel_diff = self.gs.pixel_diff
        self.fps = self.gs.fps
        self.pos = self.gs.pos
        self.sprite_sheet = SpriteSheet("numbers_gold_320x32.png", 32, self.pixel_diff, self.fps, False)
        self.number = number
        self.numbers = self.sprite_sheet.add_animation(0, 0, 10)
        self.changed = True
        self.image = self.numbers[self.number]
        self.rect = self.image.get_rect()
        self.rect.topleft = self.gs.pos
        self.left = self.gs.left
        self.child_num = child_num
        self.clean_bg = None

        width = self.image.get_width()
        width *= self.child_num

        if self.left:
            self.rect.x += width
        else:
            self.rect.x -= width

        '''store the current position'''
        self.pos = self.rect.topleft
        self.size = self.image.get_size()

    def set_number(self, number):
        """set the number to a certain value"""
        if number is not self.number:
            self.number = number
            self.changed = True

    def set_clean_rect(self):
        """copy a the clean background once"""
        if self.gs.background:
            x, y = self.pos
            w, h = self.size
            surface = self.gs.background.copy()
            self.clean_bg = surface.subsurface((x, y, w, h))

    def update(self):
        """show number"""
        if self.changed:
            if self.number < 10:
                self.image = self.numbers[self.number]

            self.changed = False

        if not self.clean_bg:
            '''
                this frame should be rendered permanently
                if it's not blitted to the background with a dirty rect
            '''
            self.dirty = 1
