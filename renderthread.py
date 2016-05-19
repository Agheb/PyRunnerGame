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

    Attributes:
        thread_is_running (bool): status of this thread
        caption (str): Window title used in windowed mode
        _screen_x (int): width of the surface
        _screen_y (int): height of the surface
        fps (int): frames per second
        fullscreen (bool): True if screen is in fullscreen mode
        upscale (bool): True if screen should be switched to lower resolution
        daemon (bool): True if this thread should be stopped with the main program
        clock (pygame.time.Clock): used to time loops
        _rects_to_update (list(Rect)): list containing all Rects which should be redrawn/updated
        screen (pygame.Surface): surface this Menu is drawn to
        _display_modes(list((x, y))): list containing all valid fullscreen resolutions

    Properties:
        rects_to_update (list(Rect)): read only access to _rects_to_update, @see add_rect_to_update
        display_modes (list(resolutions)): read only access to _display_modes
        fullscreen (bool): set fullscreen on/off, automatically updates the screen
    """

    def __init__(self, caption, width, height, fps=25, fullscreen=False, upscale=False, daemon=True):
        threading.Thread.__init__(self)
        self.thread_is_running = True
        self._caption = caption
        self._screen_x = width
        self._screen_y = height
        self.fps = fps
        self._fullscreen = fullscreen
        self.upscale = upscale
        self.daemon = daemon
        # clock thread @ fps
        self.clock = pygame.time.Clock()
        # dirty rects list to only partially update the screen
        self._rects_to_update = []
        # initialize the screen
        self.screen = None
        # initialize pygame in case it's not already
        try:
            self.update_screen()
        except pygame.error:
            pygame.init()
            self.update_screen()
        # in fullscreen mode: save all available modes for the settings
        self._display_modes = None
        self.check_display_modes()

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
                self.screen = pygame.Surface((self._screen_x, self._screen_y))
                # self.screen.get_rect().centerx = disp_screen.get_rect().centerx
                # self.screen.get_rect().centery = disp_screen.get_rect().centery
                disp_screen.blit(self.screen, (0, 0))
            else:
                # switch screen resolution to the desired one
                self.screen = pygame.display.set_mode((self._screen_x, self._screen_y), FULLSCREEN, display.bitsize)
        else:
            pygame.mouse.set_visible(True)
            self.screen = pygame.display.set_mode((self._screen_x, self._screen_y), RESIZABLE, display.bitsize)

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
                self._rects_to_update = []
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
            self._screen_x = SCREEN_MIN_X if width < SCREEN_MIN_X else width
            self._screen_y = SCREEN_MIN_Y if height < SCREEN_MIN_Y else height
        else:
            self._screen_x = WINDOW_MIN_X if width < WINDOW_MIN_X else width
            self._screen_y = WINDOW_MIN_Y if height < WINDOW_MIN_Y else height

        # update the screen
        self.update_screen()

    @property
    def caption(self):
        """ Title of the pygame window

        Returns: caption (str)
        """
        return self._caption

    @caption.setter
    def set_caption(self, caption):
        """change the screen/window resolution

        Args:
            caption (str): new window caption
        """
        if self.caption is not caption:
            self._caption = caption
        pygame.display.set_caption(self.caption)

    def fill_screen(self, fillcolor):
        """change the screen/window resolution

        Args:
            fillcolor (pygame.Color): color to fill the current surface with
        """
        self.screen.fill(fillcolor)

    @property
    def rects_to_update(self):
        return self._rects_to_update

    def add_rect_to_update(self, rects):
        """add a rect or list of rects to the rects_to_update list

        Args:
            rects (pygame.Rect or [pygame.Rect]): Rect or List of Rects to add
        """
        if len(rects) > 1:
            for i in range(0, len(rects)):
                # add the list one by one because pygame.display.update()
                # doesn't allow multi dimensional lists
                self._rects_to_update.append(rects[i])
        else:
            self._rects_to_update.append(rects)

    def blit(self, surface, pos, center=False):
        """blit a surface to the main screen

        Args:
            surface (pygame.Surface): surface to draw to the screen
            pos (int x, int y): position where to draw it at the screen (also accepts a Rect)
            center (bool): if set pos get's ignored and the surface is centered on the screen
        """
        rect = pos
        if center:
            rect = surface.get_rect()
            rect.centerx = self._screen_x / 2
            rect.centery = self._screen_y / 2
        self.screen.blit(surface, rect)

    def stop_thread(self):
        """stop the current thread by disabling its run loop"""
        self.thread_is_running = False

    @property
    def fullscreen(self):
        return self._fullscreen

    @fullscreen.setter
    def fullscreen(self, fullscreen):
        """switch fullscreen on or off

        Args:
            fullscreen (bool): fullscreen mode on (True) or off (False)
        """
        if self.fullscreen is not fullscreen:
            self._fullscreen = fullscreen
            self.update_screen()

    def check_display_modes(self):
        """store all available display modes in fullscreen

        Cave: should only be run once on (full)screen initialization because it causes heavy flickering
        """
        if self.fullscreen:
            self._display_modes = pygame.display.list_modes()

    @property
    def display_modes(self):
        """return the saved list of display modes

        Returns: display_modes ([(x, y)]): tuples of width and heights in a list
        """
        return self._display_modes

