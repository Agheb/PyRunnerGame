#!/usr/bin/python
# -*- coding: utf-8 -*-
"""main pyRunner class which initializes all sub classes and threads"""
# Python 2 related fixes
from __future__ import division
# universal imports
import pygame
from pygame.locals import *
import sys
import os
# pyRunner subclasses
from pyrunner_classes import *


class PyRunner(object):
    """main PyRunner Class"""

    def __init__(self):
        """initialize the game"""
        '''important settings'''
        self.game_is_running = True
        # initialize the settings
        self.config = MainConfig()
        '''init the audio subsystem prior to anything else'''
        self.music_thread = MusicMixer(self.config.play_music, self.config.vol_music,
                                       self.config.play_sfx, self.config.vol_sfx, self.config.fps)
        self.music_thread.background_music = ('time_delay.wav', 1)
        self.music_thread.start()
        '''init the main screen'''
        self.render_thread = RenderThread(self.config.name, self.config.screen_x, self.config.screen_y, self.config.fps,
                                          self.config.fullscreen, self.config.switch_resolution)
        self.render_thread.fill_screen(BACKGROUND)
        self.render_thread.start()
        # set the background image
        # self.bg_image = pygame.image.load(os.path.join('./resources/images/', 'lode2.gif')).convert()
        '''init the main menu'''
        self.bg_image = pygame.Surface((self.config.screen_x, self.config.screen_y))
        self.level = Level("./resources/levels/scifi.tmx", self.bg_image)
        self.physics = Physics(self.render_thread)
        # self.bg_image.blit(self.level, self.level.get_rect())
        self.render_thread.blit(self.bg_image, None, True)
        self.menu = MainMenu(self)
        self.controller = Controller(self.physics.player,self.config)

    def quit_game(self, shutdown=True):
        """quit the game"""
        self.game_is_running = False
        self.config.write_settings()
        self.render_thread.stop_thread()
        self.music_thread.stop_thread()
        pygame.quit()
        if shutdown:
            exit()

    def restart_program(self):
        """Restarts the current program"""
        self.quit_game(False)
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def player_test(self):
        if self.in_menu:
            self.show_menu(False)
        surface = pygame.Surface((self.screen_x, self.screen_y), SRCALPHA)
        rects = []
        # player = pygame.draw.circle(surface, color, )
        rects.append(player)
        print("draw player")
        self.render_thread.blit(surface, None, True)
        self.render_thread.add_rect_to_update(rects, surface, None, True)
        self.render_thread.refresh_screen(True)

    def start_game(self):
        """main game loop"""
        # Main loop relevant vars
        clock = pygame.time.Clock()

        # switch music (test)
        self.music_thread.background_music = ('summers_end_acoustic.aif', 0)
        # we should probably save all game sounds as variables
        sound_shoot = pygame.mixer.Sound(self.music_thread.get_full_path_sfx('9_mm_gunshot-mike-koenig-123.wav'))

        while self.game_is_running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.quit_game()
                elif event.type == KEYDOWN:
                    key = event.key
                    '''key pressing events'''
                    if self.menu.in_menu:
                        self.menu.key_actions(key)
                    else:
                        if key == K_ESCAPE:
                            self.menu.show_menu(True)
                        else:
                            self.controller.interpret_key(key)
            # save cpu resources
            self.physics.update()
            clock.tick(self.config.fps)


if __name__ == "__main__":
    pyrunner = PyRunner()
    # start the 4 in a row game
    pyrunner.start_game()
