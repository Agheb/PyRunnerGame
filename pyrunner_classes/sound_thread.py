#!/usr/bin/python
# -*- coding: utf-8 -*-
"""thread taking care of all sound output"""
# Python 2 related fixes
from __future__ import division
# universal imports
import threading
import pygame
import os

'''constants'''
# relative folder paths
MUSIC_PATH = "./resources/music/"
SOUND_PATH = "./resources/sound_fx/"


class MusicMixer(threading.Thread):
    """a thread handling all the sound fx and music"""

    def __init__(self, play_music=True, music_volume=10, play_sfx=True, sfx_volume=10, fps=25, daemon=True):
        """a separate daemon thread that keeps playing music and sound in the background.
           if there are not enough sound channels available this thread will dynamically increase
           the amount of channels so no sound lag should occur if your hardware can handel it

        Args:
            play_music (bool): enable or disable background music
            music_volume (int): 0 to 10; set the music volume from 10 to 100%
            play_sfx (bool): enable or disable all sound fx
            sfx_volume (int): 0 to 10; set the sound fx volume on all channels from 10 to 100%
            fps (int): use this to sync the speed of the main loop (ticked at fps) along different classes
            daemon (bool): define if this thread should quit as soon as the main program quits
        """
        threading.Thread.__init__(self)
        # pre-init the mixer to avoid sound lag
        # had to reduce the buffer to 1024 for Linux not to lag too much
        pygame.mixer.pre_init(22050, -16, 2, 1024)
        pygame.mixer.init()
        self.thread_is_running = True
        self.fps = fps
        self.clock = pygame.time.Clock()
        self.daemon = daemon
        # music related values
        self._background_music = None
        self._music = []
        self._play_music = None
        self.play_music = play_music
        self._music_volume = None
        self.music_volume = music_volume
        # sound effect related values
        self.play_sfx = play_sfx
        self._sound_fx_volume = None
        self.sfx_volume = sfx_volume

    def run(self):
        """Thread main run function

        Overrides: threading.Thread.run()
        """
        music_counter = 0
        while self.thread_is_running:
            if self.play_music and self._music and not pygame.mixer.music.get_busy():
                '''play the next song'''
                self.background_music = self._music[music_counter]
                music_counter = music_counter + 1 if music_counter < len(self._music) - 1 else 0
            # don't waste too many cpu cycles
            self.clock.tick(self.fps)

    def stop_thread(self):
        """fade out music when thread stops"""
        self.thread_is_running = False
        pygame.mixer.music.fadeout(1500)

    def play_sound(self, file, loop):
        """use this class to make this thread play a sound file.
           either pass a string containing the file name (the file must be located in SOUND_PATH)
           or a pygame.mixer.Sound file which will be passed on directly.


        Args:
            file (str or pygame.mixer.Sound): file which should be played (instantly)
            :param file: name of the file that should be played
            :param loop: Loop plays the file infinitily when True.
        """
        loop = loop

        if self.play_sfx:
            try:
                channel = pygame.mixer.find_channel()
                if channel and not loop:
                    channel.play(file)
                elif channel and loop:
                    channel.play(file, loops=-1)
                else:
                    '''if there's no free channels we need to add some more'''
                    num_channels = old_channels = pygame.mixer.get_num_channels()
                    num_channels += 8
                    '''print some informational debugging string to the console'''
                    print("Increased the number of sound channels from %(old_channels)s to %(num_channels)s" % locals())
                    pygame.mixer.set_num_channels(num_channels)
                    '''set the volume for all channels, else the new ones differ'''
                    self.sfx_volume = self.sfx_volume
                    # retry
                    self.play_sound(file)
            except TypeError:
                '''if necessary parse a filename string to a full path and load it as pygame.mixer.Sound'''
                # self.play_sound(pygame.mixer.Sound(self.get_full_path_sfx(file)))
                # TODO: when this exception is called the game breaks

    @staticmethod
    def get_full_path_music(file):
        """helper function to get a full path for a music file in MUSIC_PATH

        Args:
            file (str): the filename of the requested file

        Returns: the full (relative) path as string
        """
        return os.path.join(MUSIC_PATH, file)

    @staticmethod
    def get_full_path_sfx(file):
        """helper function to get a full path for a sound file in SOUND_PATH

        Args:
            file (str): the filename of the requested file

        Returns: the full (relative) path as string
        """
        return os.path.join(SOUND_PATH, file)

    def clear_background_music(self):
        """helper function to stop all currently playing music and clearing the playlist
           should be used if you switch levels etc. and want to switch the atmosphere
        """
        pygame.mixer.music.fadeout(50)
         # pygame.mixer.music.stop()
        self._music = []

    def clear_sounds(self):
        """helper function to clear all sound effects. Music keeps playing until clear_background_music is called"""
        pygame.mixer.stop()

    @property
    def background_music(self):
        """
        Returns: the filename of the currently playing music
        """
        return self._background_music

    @background_music.setter
    def background_music(self, file_loops):
        """set/add a file to the background music playlist

            usage: background_music('filename.wav', 3) -> will loop the file 4 times before playing the next song

        Args:
            file_loops (tuple): contains the filename (str) and loop instructions (int) of the file you want to play
        """
        file, loops = file_loops
        # add the directory path
        file = self.get_full_path_music(file)

        if file_loops not in self._music:
            '''store the file name and loop instruction in the playlist'''
            self._music.append(file_loops)
        if self.play_music:
            try:
                if not pygame.mixer.music.get_busy():
                    self._background_music = file
                    pygame.mixer.music.load(file)
                    '''play background music'''
                    pygame.mixer.music.play(loops)  # plays once more than expected
                else:
                    '''add the file to the queue playing up next'''
                    pygame.mixer.music.queue(file)
                    '''fading blocks the whole pygame process so it's no useful option'''
                    # and gently fade out (3 seconds)
                    # pygame.mixer.music.fadeout(3000)
                    '''stopping is too harsh but the only option if music runs in loop'''
                    # pygame.mixer.music.stop()
                    # pygame.mixer.music.load(self._background_music)
            except pygame.error:
                print("Error loading music file %s" % file)
                self._music.remove(file_loops)
                # raise

    @property
    def play_music(self):
        """
        Returns: a boolean telling if background music playback is enabled/disabled
        """
        return self._play_music

    @play_music.setter
    def play_music(self, play_music):
        """ enable/disable background music playback

        Args:
            play_music (bool): enable music = True, False else
        """
        self._play_music = play_music

        '''fade out music if it's turned off, half a second is ok for blocking'''
        if not play_music:
            pygame.mixer.music.fadeout(500)

    @property
    def music_volume(self):
        """
        Returns: the current background music volume represented as int from 0 to 10 (100%)
        """
        return self._music_volume

    @music_volume.setter
    def music_volume(self, volume):
        """set the background music volume to the desired level

        Args:
            volume (int): value from 0 to 10 (=100%)
        """
        if 0 <= volume <= 10:
            '''pygame uses values from 0.0 to 1.0'''
            vol = volume / 10
            self._music_volume = int(volume)
            pygame.mixer.music.set_volume(vol)
        else:
            print("Volume value must be between 0 and 10")

    @property
    def sfx_volume(self):
        """
        Returns: the current sound fx volume represented as int from 0 to 10 (100%)
        """
        return self._sound_fx_volume

    @sfx_volume.setter
    def sfx_volume(self, volume):
        """set the background music volume to the desired level

        Args:
            volume (int): value from 0 to 10 (=100%)
        """
        if 0 <= volume <= 10:
            '''pygame uses values from 0.0 to 1.0'''
            vol = volume / 10
            self._sound_fx_volume = int(volume)
            '''apply these settings to all existing sound channels'''
            for num in range(pygame.mixer.get_num_channels()):
                pygame.mixer.Channel(num).set_volume(vol)
        else:
            print("Volume value must be between 0 and 10")
