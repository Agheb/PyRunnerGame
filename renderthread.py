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
    """Main Thread which renders all drawings to the screen

        Args:
            caption (str): Window Title to use in windowed mode
            width (int): screen/window width
            height (int): screen/window height
            fps (Optional[int]): frames per second (how often the screen will be redrawn per second)
            fullscreen (Optional[bool]): run in fullscreen or windowed mode
            upscale (Optional[bool]): don't switch screen resolution but render on smaller surface
            daemon (Optional[bool]): quit this thread if main program quits
    """

    def __init__(self, caption, width, height, fps=25, fullscreen=False, upscale=False, daemon=True):
        threading.Thread.__init__(self)
        self.thread_is_running = True
        self.caption = caption
        self.screen_x = width
        self.screen_y = height
        self.fps = fps
        self.fullscreen = fullscreen
        self.upscale = upscale
        self.daemon = daemon
        # clock thread @ fps
        self.clock = pygame.time.Clock()
        # dirty rects list to only partially update the screen
        self.rects_to_update = []
        # initialize the screen
        self.screen = None
        # initialize pygame in case it's not already
        try:
            self.update_screen()
        except pygame.error:
            pygame.init()
            self.update_screen()
        # in fullscreen mode: save all available modes for the settings
        self.display_modes = None
        self.check_display_modes()
        self.set_caption(self.caption)

    def run(self):
        """Thread main run function

            Overrides: threading.Thread.run()
        """
        run_counter = 0

        while self.thread_is_running:
            if self.fps * 10 <= run_counter:
                # completely refresh screen once every 10 seconds
                self.refresh_screen(True)
                run_counter = 0
            else:
                # else only if necessary
                if self.rects_to_update:
                    self.refresh_screen()
                run_counter += 1

            self.clock.tick(self.fps)

    def update_screen(self):
        """switch to windowed or fullscreen mode"""
        display = pygame.display.Info()

        if self.fullscreen:
            pygame.mouse.set_visible(False)
            # if upscaling is set, render to a smaller surface but show it on the full screen
            if not self.upscale:
                disp_screen = pygame.display.set_mode((display.current_w, display.current_h), FULLSCREEN, display.bitsize)
                self.screen = pygame.Surface((self.screen_x, self.screen_y))
                # self.screen.get_rect().centerx = disp_screen.get_rect().centerx
                # self.screen.get_rect().centery = disp_screen.get_rect().centery
                disp_screen.blit(self.screen, (0, 0))
            else:
                # switch screen resolution to the desired one
                self.screen = pygame.display.set_mode((self.screen_x, self.screen_y), FULLSCREEN, display.bitsize)
        else:
            pygame.mouse.set_visible(True)
            self.screen = pygame.display.set_mode((self.screen_x, self.screen_y), RESIZABLE, display.bitsize)

        self.refresh_screen(True)

    def refresh_screen(self, complete_screen=False):
        """refresh the pygame screen/window"""
        try:
            # redraw the whole screen
            if not self.rects_to_update or complete_screen:
                pygame.display.update()
            else:
                # only update the changed rects
                pygame.display.update(self.rects_to_update)
                self.rects_to_update = []
        except pygame.error:
            # OpenGL can only redraw the whole screen
            pygame.display.flip()

    def set_resolution(self, width, height):
        """change the screen/window resolution

            Args:
                width (int): screen/window width
                height (int): screen/window height
        """
        if self.fullscreen:
            self.screen_x = SCREEN_MIN_X if width < SCREEN_MIN_X else width
            self.screen_y = SCREEN_MIN_Y if height < SCREEN_MIN_Y else height
        else:
            self.screen_x = WINDOW_MIN_X if width < WINDOW_MIN_X else width
            self.screen_y = WINDOW_MIN_Y if height < WINDOW_MIN_Y else height

        # update the screen
        self.update_screen()

    def set_caption(self, text):
        """change the screen/window resolution

            Args:
                text (str): new window caption
        """
        if self.caption is not text:
            self.caption = text
        pygame.display.set_caption(self.caption)

    def fill_screen(self, fillcolor):
        """change the screen/window resolution

            Args:
                fillcolor (pygame.Color): color to fill the current surface with
        """
        self.screen.fill(fillcolor)

    def add_rect_to_update(self, rects):
        """add a rect or list of rects to the rects_to_update list

            Args:
                rects (pygame.Rect or [pygame.Rect]): Rect or List of Rects to add
        """
        if len(rects) > 1:
            for i in range(0, len(rects)):
                # add the list one by one because pygame.display.update()
                # doesn't allow multi dimensional lists
                self.rects_to_update.append(rects[i])
        else:
            self.rects_to_update.append(rects)

    def get_screen(self):
        """returns the current drawing surface / main screen

            Returns:
                screen (pygame.Surface): Surface on which all rendering takes place
        """
        return self.screen

    def stop_thread(self):
        """stop the current thread by disabling its run loop"""
        self.thread_is_running = False

    def set_fullscreen(self, bool_full):
        """switch fullscreen on or off

            Args:
                bool_full (bool): fullscreen on (True) or off (False)
        """
        if bool_full is not self.fullscreen:
            self.fullscreen = bool_full
            self.update_screen()

    def check_display_modes(self):
        """get all available display modes in fullscreen"""
        if self.fullscreen:
            self.display_modes = pygame.display.list_modes()

    def get_display_modes(self):
        """return the saved list of display modes

            Returns: display_modes ([(x, y)]): tuples of width and heights in a list
        """
        return self.display_modes
