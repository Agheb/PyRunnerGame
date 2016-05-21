import threading
import os
import pygame
from pygame.locals import *

MUSIC_PATH = "./resources/music/"
SOUND_PATH = "./resources/sound_fx/"


class MusicMixer(threading.Thread):

    def __init__(self, play_music=True, music_volume=10, play_sfx=True, sfx_volume=10, fps=25, daemon=True):
        threading.Thread.__init__(self)
        pygame.mixer.pre_init(44100, -16, 2, 4096)
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
                file_loops = self._music[music_counter]
                self.background_music = file_loops
                music_counter = music_counter + 1 if music_counter < len(self._music) - 1 else 0
            self.clock.tick(self.fps)

    def stop_thread(self):
        """fade out music when thread stops"""
        self.thread_is_running = False
        pygame.mixer.music.fadeout(1500)

    def _play_sounds(self, sound):
        if self.play_sfx:
            channel = pygame.mixer.find_channel()
            if channel:
                if not channel.get_busy():
                    channel.play(sound)
                else:
                    channel.queue(sound)
            else:
                '''if there's no free channels we need to add some more'''
                num_channels = old_channels = pygame.mixer.get_num_channels()
                num_channels += 8
                print("Increased the number of sound channels from " + str(old_channels) + " to " + str(num_channels))
                pygame.mixer.set_num_channels(num_channels)
                # retry
                return self._play_sounds(sound)

    def play_sound(self, file):
        if self.play_sfx:
            if type(file) is str:
                '''if necessary parse a filename string to a full path and load it as pygame.mixer.Sound'''
                file = pygame.mixer.Sound(self.get_full_path_sfx(file))

            if type(file) is pygame.mixer.Sound:
                '''only add pygame.mixer.Sound files to the queue'''
                self._play_sounds(file)

    @staticmethod
    def get_full_path_music(file):
        return os.path.join(MUSIC_PATH, file)

    @staticmethod
    def get_full_path_sfx(file):
        return os.path.join(SOUND_PATH, file)

    def clear_background_music(self):
        pygame.mixer.music.stop()
        self._music = []

    @property
    def background_music(self):
        return self._background_music

    @background_music.setter
    def background_music(self, file_loops):
        file, loops = file_loops
        # add the directory path
        file = self.get_full_path_music(file)

        if file_loops not in self._music:
            # only store the file name, this re-adds music from the main loop at the end of the list
            self._music.append(file_loops)
        if self.play_music:
            try:
                if not pygame.mixer.music.get_busy():
                    self._background_music = file
                    pygame.mixer.music.load(file)
                    '''play background music'''
                    pygame.mixer.music.play(loops)  # plays once per default
                else:
                    '''add the file to the queue playing up next'''
                    pygame.mixer.music.queue(file)
                    '''fading blocks the whole pygame process :/'''
                    # and gently fade out (3 seconds)
                    # pygame.mixer.music.fadeout(3000)
                    '''stopping is too harsh but the only option if music runs in loop'''
                    # pygame.mixer.music.stop()
                    # pygame.mixer.music.load(self._background_music)
            except pygame.error:
                print(str("Error loading music file " + str(file)))
                # pass the exact error
                raise

    @property
    def play_music(self):
        return self._play_music

    @play_music.setter
    def play_music(self, play_music):
        self._play_music = play_music

        if not play_music:
            pygame.mixer.music.fadeout(500)

    @property
    def music_volume(self):
        return self._music_volume

    @music_volume.setter
    def music_volume(self, volume):
        if 0 <= volume <= 10:
            vol = volume / 10
            self._music_volume = int(volume)
            pygame.mixer.music.set_volume(vol)
        else:
            print("Volume value must be between 0 and 10")

    @property
    def sfx_volume(self):
        return self._sound_fx_volume

    @sfx_volume.setter
    def sfx_volume(self, volume):
        if 0 <= volume <= 10:
            vol = volume / 10
            self._sound_fx_volume = int(volume)
            for num in range(pygame.mixer.get_num_channels()):
                channel = pygame.mixer.Channel(num)
                channel.set_volume(vol)
        else:
            print("Volume value must be between 0 and 10")
