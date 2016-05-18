import pygame
import threading
from pygame.locals import *

# Minimum Fullscreen Resolution
SCREEN_MIN_X = 640
SCREEN_MIN_Y = 480
# Minimum Windowed Resolution
WINDOW_MIN_X = SCREEN_MIN_X - 40
WINDOW_MIN_Y = SCREEN_MIN_Y - 80


class RenderThread(threading.Thread):

    def __init__(self, caption, width, height, fps=25, fullscreen=False, upscale=False, daemon=True):
        threading.Thread.__init__(self)
        pygame.init()
        self.thread_is_running = True
        self.caption = caption
        self.screen_x = width
        self.screen_y = height
        self.fps = fps
        self.fullscreen = fullscreen
        self.upscale = upscale
        self.daemon = daemon
        self.display_modes = None
        self.clock = pygame.time.Clock()
        self.rects_to_update = []
        self.screen = None
        self.update_screen()
        self.check_display_modes()
        pygame.display.set_caption(self.caption)

    def run(self):
        runcounter = 0

        while self.thread_is_running:
            if self.fps * 10 <= runcounter:
                # completely refresh screen once every 10 seconds
                self.refresh_screen(True)
                runcounter = 0
            else:
                # else only if necessary
                if self.rects_to_update:
                    self.refresh_screen()
                runcounter += 1

            self.clock.tick(self.fps)

    def update_screen(self):
        """switch to fullscreen mode"""

        display = pygame.display.Info()

        if self.fullscreen:
            pygame.mouse.set_visible(False)
            if self.upscale:
                s_width, s_height = display.current_w, display.current_h
                self.screen_x, self.screen_y = s_width, s_height
            self.screen = pygame.display.set_mode((self.screen_x, self.screen_y), FULLSCREEN, display.bitsize)
        else:
            pygame.mouse.set_visible(True)
            self.screen = pygame.display.set_mode((self.screen_x, self.screen_y), RESIZABLE, display.bitsize)

        self.refresh_screen(True)

    def refresh_screen(self, complete_screen=False):
        """refresh the pygame screen/window"""
        try:
            # screen.fill(BACKGROUND)

            if not self.rects_to_update or complete_screen:
                pygame.display.update()
            else:
                pygame.display.update(self.rects_to_update)
                self.rects_to_update = []

        except pygame.error:
            # OpenGL can only redraw the whole screen
            pygame.display.flip()

    def set_resolution(self, width, height):

        if self.fullscreen:
            self.screen_x = SCREEN_MIN_X if width < SCREEN_MIN_X else width
            self.screen_y = SCREEN_MIN_Y if height < SCREEN_MIN_Y else height
        else:
            self.screen_x = WINDOW_MIN_X if width < WINDOW_MIN_X else width
            self.screen_y = WINDOW_MIN_Y if height < WINDOW_MIN_Y else height

        # update the screen
        self.update_screen()

    def set_caption(self, text):
        self.caption = text
        pygame.display.set_caption(self.caption)

    def fill_screen(self, fillcolor):
        self.screen.fill(fillcolor)

    def add_rect_to_update(self, rects):
        if len(rects) > 1:
            for i in range(0, len(rects)):
                self.rects_to_update.append(rects[i])
        else:
            self.rects_to_update.append(rects)

    def get_screen(self):
        return self.screen

    def stop_thread(self):
        self.thread_is_running = False

    def set_fullscreen(self, bool_full):
        if bool_full is not self.fullscreen:
            self.fullscreen = bool_full
            self.update_screen()

    def check_display_modes(self):
        if self.fullscreen:
            self.display_modes = pygame.display.list_modes()

    def get_display_modes(self):
        return self.display_modes
