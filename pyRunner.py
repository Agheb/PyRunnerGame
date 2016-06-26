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
import argparse
import logging
# pyRunner subclasses
from pyrunner_classes import *

# interpret command line ags
parser = argparse.ArgumentParser(description='Testing')
parser.add_argument('--log',
                    help='pass the log level desired (info, debug,...)', type=str)
args = parser.parse_args()

# set log level
# specify --log=DEBUG or --log=debug
if args.log is not None:
    numeric_level = getattr(logging, args.log.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % args.log)
    logging.basicConfig(level=numeric_level)


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
        '''init the level and main game physics'''
        self.bg_surface = pygame.Surface((self.config.screen_x, self.config.screen_y))
        self.level = None
        self.physics = None
        self.load_level(0)
        '''init the main menu'''
        self.network_connector = NetworkConnector()
        self.menu = MainMenu(self, self.network_connector)
        self.controller = Controller(self.physics, self.config, self.network_connector)

    def load_level(self, levelnumber):
        """load another level"""
        self.level = Level(self.bg_surface,levelnumber)
        self.physics = Physics(self.render_thread.screen, self.level)

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
                elif event.type == KEYUP:
                    '''key pressing events'''
                    if not self.menu.in_menu:
                        self.controller.release_key(event.key)
            # save cpu resources
            if not self.menu.in_menu:
                self.render_thread.add_rect_to_update(self.physics.update())
            clock.tick(self.config.fps)


if __name__ == "__main__":
    pyrunner = PyRunner()
    # start the pyrunner game
    pyrunner.start_game()
