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

    START_LEVEL = "./resources/levels/level1.tmx"

    def __init__(self):
        """initialize the game"""
        '''important settings'''
        self.game_is_running = True
        # initialize the settings
        self.config = MainConfig()
        self.fps = self.config.fps
        '''init the audio subsystem prior to anything else'''
        self.music_thread = MusicMixer(self.config.play_music, self.config.vol_music,
                                       self.config.play_sfx, self.config.vol_sfx, self.fps)
        self.music_thread.background_music = ('thememusic.ogg', 1)
        self.music_thread.start()
        '''init the main screen'''
        self.render_thread = RenderThread(self.config.name, self.config.screen_x, self.config.screen_y, self.fps,
                                          self.config.fullscreen, self.config.switch_resolution)
        self.render_thread.fill_screen(BACKGROUND)
        self.bg_surface = pygame.Surface((self.config.screen_x, self.config.screen_y))
        self.render_thread.bg_surface = self.bg_surface
        self.render_thread.start()
        self.surface = self.render_thread.screen
        '''init the level and main game physics'''
        self.network_connector = None
        self.menu = None
        self.level = None
        self.physics = None
        self.controller = None
        self.load_level(self.START_LEVEL, self.music_thread)
        '''init the main menu'''
        self.level_exit = False
        self.loading_level = False
        self.game_over = False

    def load_level(self, path,sound_thread):
        """load another level"""
        self.loading_level = True
        '''clear all sprites from an old level if present'''
        if self.level:
            '''clear all old sprites'''
            Player.group.empty()
            WorldObject.group.empty()
            WorldObject.removed.empty()
            self.level_exit = False
            # don't remove the GoldScore.scores as they should stay for a level switch
        '''load the new level'''
        self.level = Level(self.bg_surface, path,sound_thread, self.fps)
        '''bug fix for old background appearing on the screen'''
        WorldObject.group.clear(self.level.surface, self.level.background)
        '''change the dirty rect for fps display'''
        self.render_thread.clear_fps_rect()
        '''Linux not refreshing the background bug'''
        self.render_thread.blit(self.level.surface, None, True)
        '''refresh the whole screen'''
        self.render_thread.refresh_screen(True)


        if not self.network_connector:
            self.network_connector = NetworkConnector(self, self.level)
            self.menu = MainMenu(self, self.network_connector)
        else:
            self.network_connector.level = self.level

        '''and the controller instance'''
        self.controller = Controller(self.config, self.network_connector)
        self.game_over = False
        self.loading_level = False

    def quit_game(self, shutdown=True):
        """quit the game"""
        self.game_is_running = False
        self.config.write_settings()
        self.render_thread.stop_thread()
        self.music_thread.stop_thread()
        self.network_connector.quit()
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
        self.music_thread.background_music = ('thememusic.ogg', 0)
        # we should probably save all game sounds as variables
        sound_shoot = pygame.mixer.Sound(self.music_thread.get_full_path_sfx('coin.wav'))

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
            if not self.menu.in_menu and not self.loading_level:
                self.render_thread.add_rect_to_update(self.render_game())

                if self.game_over:
                    self.menu.set_current_menu(self.menu.game_over)

            self.network_connector.update()

            clock.tick(self.fps)

    def render_game(self):
        """render all game related content"""
        '''update all sprite groups'''
        GoldScore.scores.update()
        Player.group.update()
        '''store all screen changes, draw & update the level'''
        rects = self.level.update()
        '''blit the level surface to the main screen'''
        self.render_thread.blit(self.level.surface, None, True)
        '''draw the player and scores'''
        rects.append(Player.group.draw(self.surface))
        rects.append(GoldScore.scores.draw(self.surface))
        '''clean up the dirty background'''
        self.level.clear(self.surface)

        '''check if all gold got collected and spawn a exit gate if there's none left'''
        if not self.level_exit and not any(sprite.collectible for sprite in WorldObject.group):
            try:
                self.level_exit = ExitGate(self.level.next_level_pos, self.level.PLAYERS[0], 32,
                                           self.level.pixel_diff, self.fps)
            except AttributeError:
                self.game_over = True

                for player in Player.group:
                    if player.is_human:
                        player.reached_exit = True

                self.level_exit = True

        '''check if all players are still alive'''
        if not any(player.is_human for player in Player.group):
            if not self.level_exit:
                '''show the game over menu with player gold scores'''
                self.game_over = True
                self.game_over_menu()
            else:
                '''load the next level, recreate the players and bots etc.'''
                self.load_level(self.level.next_level)

        return rects

    def game_over_menu(self):
        """create the game over menu"""
        found_one = False
        for score in GoldScore.scores:
            if not score.child_num:
                if not found_one:
                    found_one = True
                    self.menu.game_over.add_item(MenuItem("Collected Gold"))
                score_str = "Player %s: %s coins" % (score.gid, score.gold)
                self.menu.game_over.add_item(MenuItem(score_str))

if __name__ == "__main__":
    pyrunner = PyRunner()
    # start the pyrunner game
    pyrunner.start_game()
