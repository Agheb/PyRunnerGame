#!/usr/bin/python
# -*- coding: utf-8 -*-
# Python 2 related fixes
from __future__ import division
# universal imports
import pygame
from pygame.locals import *
import os
# pyRunner subclasses
from pyrunner_classes import *


class PyRunner(object):
    """main PyRunner Class

       This class runs the whole game an initializes all necessary values
    """

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
        self.bg_image = pygame.image.load(os.path.join('./resources/images/', 'lode2.gif')).convert()
        '''init the main menu'''
        self.menu = MainMenu(self.config, self.render_thread, self.music_thread, self.bg_image)


    def start_game(self):
        """main game loop"""
        # Main loop relevant vars
        clock = pygame.time.Clock()

        # switch music (test)
        self.music_thread.background_music = ('summers_end_acoustic.aif', 0)
        # we should probably save all game sounds as variables
        sound_shoot = pygame.mixer.Sound(self.music_thread.get_full_path_sfx('9_mm_gunshot-mike-koenig-123.wav'))

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.menu.quit_game()
                elif event.type == KEYDOWN:
                    key = event.key
                    '''key pressing events'''
                    if self.menu.in_menu:
                        if key == K_SPACE:
                            self.music_thread.play_sound(sound_shoot)
                        elif key == K_LSHIFT:
                            self.music_thread.play_sound('unscrew_lightbulb-mike-koenig.wav')
                        else:
                            self.menu.key_actions(key)
                    else:
                        """controls and key settings if the game is in foreground"""
                        if key == K_ESCAPE:
                            self.menu.show_menu(True)
                        # TODO move both players
                        elif key == self.config.p1_left:
                            print("Player 1 moves left")
                        elif key == self.config.p1_right:
                            print("Player 1 moves right")
                        elif key == self.config.p1_up:
                            print("Player 1 moves up")
                        elif key == self.config.p1_down:
                            print("Player 1 moves down")
                        # TODO actions for both players
                        elif key == self.config.p1_action_l:
                            print("Player 1 digs left")
                        elif key == self.config.p1_action_r:
                            print("Player 1 digs right")
                        elif key == self.config.p1_interact:
                            print("Player 1 interacts")
                        elif key == self.config.p1_taunt:
                            print("Player 1 taunts")
                        # TODO the same for player 2
                        elif key == self.config.p2_left:
                            print("Player 2 moves left")
                        elif key == self.config.p2_right:
                            print("Player 2 moves right")
                        elif key == self.config.p2_up:
                            print("Player 2 moves up")
                        elif key == self.config.p2_down:
                            print("Player 2 moves down")
                        # TODO actions for both players
                        elif key == self.config.p2_action_l:
                            print("Player 2 digs left")
                        elif key == self.config.p2_action_r:
                            print("Player 2 digs right")
                        elif key == self.config.p2_interact:
                            print("Player 2 interacts")
                        elif key == self.config.p2_taunt:
                            print("Player 2 taunts")

            # save cpu resources
            clock.tick(self.config.fps)


if __name__ == "__main__":
    pyrunner = PyRunner()
    # start the 4 in a row game
    pyrunner.start_game()
