import threading
import os
import pygame
from pygame.locals import *

MUSIC_PATH = "./resources/music/"
SOUND_PATH = "./resources/sound_fx/"


class MusicMixer(threading.Thread):

    def __init__(self, music_volume=10, sfx_volume=10, fps=25, daemon=True):
        threading.Thread.__init__(self)
        pygame.mixer.pre_init(44100, -16, 2, 4096)
        pygame.mixer.init()
        self.fps = fps
        self.clock = pygame.time.Clock()
        self.daemon = daemon
        self._background_music = None
        self._music = []
        self._music_volume = None
        self.music_volume = music_volume
        self._sound_fx_queue = []
        self._sound_fx_volume = None
        self.sound_fx_volume = sfx_volume

    def run(self):
        """Thread main run function

        Overrides: threading.Thread.run()
        """
        music_counter = 0
        while True:
            if self._sound_fx_queue:
                self._play_sounds()
            if self._music and not pygame.mixer.music.get_busy():
                '''play the next song'''
                file_loops = self._music[music_counter]
                self.background_music = file_loops
                music_counter = music_counter + 1 if music_counter < len(self._music) - 1 else 0
            self.clock.tick(self.fps)

    def _play_sounds(self):
        for sound in range(len(self._sound_fx_queue)):
            channel = pygame.mixer.find_channel()
            if not channel.get_busy():
                channel.play(self._sound_fx_queue.pop(sound))
            else:
                channel.queue(self._sound_fx_queue.pop(sound))

    def play_sound(self, file):
        full_path = os.path.join(SOUND_PATH, file)
        self._sound_fx_queue.append(full_path)
        self._play_sounds()

    def stop_background_music(self):
        pygame.mixer.music.stop()
        self._music = []

    @property
    def background_music(self):
        return self._background_music

    @background_music.setter
    def background_music(self, file_loops):
        file, loops = file_loops
        # add the directory path
        file = os.path.join(MUSIC_PATH, file)

        if file_loops not in self._music:
            # only store the file name, this re-adds music from the main loop at the end of the list
            self._music.append(file_loops)
            print(str(file_loops))
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
    def sound_fx_volume(self):
        return self._sound_fx_volume

    @sound_fx_volume.setter
    def sound_fx_volume(self, volume):
        if 0 <= volume <= 10:
            vol = volume / 10
            self._sound_fx_volume = int(volume)
            for num in range(pygame.mixer.get_num_channels()):
                channel = pygame.mixer.Channel(num)
                channel.set_volume(vol)
        else:
            print("Volume value must be between 0 and 10")
