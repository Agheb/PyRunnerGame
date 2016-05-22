#!/usr/bin/python
# -*- coding: utf-8 -*-
# Python 2 related fixes
from __future__ import division
# universal imports
import pygame
import threading
from pygame.locals import *

'''constants'''
# Minimum Fullscreen Resolution
SCREEN_MIN_X = 640
SCREEN_MIN_Y = 480
# Minimum Windowed Resolution
WINDOW_MIN_X = SCREEN_MIN_X - 40
WINDOW_MIN_Y = SCREEN_MIN_Y - 80
# Colors
WHITE = (255, 255, 255)
BACKGROUND = (200, 200, 200)


class RenderThread(threading.Thread):
    """Main Thread which renders all drawings to the screen

    Args:
        caption (str): Window Title to use in windowed mode
        width (int): screen/window width
        height (int): screen/window height
        fps (Optional[int]): frames per second (how often the screen will be redrawn per second)
        fullscreen (Optional[bool]): run in fullscreen or windowed mode
        switch_resolution (Optional[bool]): don't switch screen resolution but render on smaller surface
        daemon (Optional[bool]): quit this thread if main program quits

    Attributes:
        thread_is_running (bool): status of this thread
        caption (str): Window title used in windowed mode
        _screen_x (int): width of the surface
        _screen_y (int): height of the surface
        fps (int): frames per second
        fullscreen (bool): True if screen is in fullscreen mode
        switch_resolution (bool): True if screen should be switched to lower resolution
        daemon (bool): True if this thread should be stopped with the main program
        clock (pygame.time.Clock): used to time loops
        _rects_to_update (list(Rect)): list containing all Rects which should be redrawn/updated
        _screen (pygame.Surface): surface this Menu is drawn to
        _display_modes(list((x, y))): list containing all valid fullscreen resolutions

    Properties:
        screen (pygame.Surface): the main surface to draw to
        rects_to_update (list(Rect)): read only access to _rects_to_update, @see add_rect_to_update
        display_modes (list(resolutions)): read only access to _display_modes
        fullscreen (bool): set fullscreen on/off, automatically updates the screen
    """

    def __init__(self, caption, width, height, fps=25, fullscreen=False, switch_resolution=False, daemon=True):
        threading.Thread.__init__(self)
        self.thread_is_running = True
        self._caption = None
        self._screen_x = width
        self._screen_y = height
        self.fps = fps
        self._fullscreen = fullscreen
        self.switch_resolution = switch_resolution
        self.daemon = daemon
        self.lock = threading.Lock()
        # clock thread @ fps
        self.clock = pygame.time.Clock()
        # dirty rects list to only partially update the screen
        self._rects_to_update = []
        # initialize the screen
        self._screen = None
        self._force_refresh = False
        self._updating_screen = False
        self.bg_surface = None
        self._fps_surface = None
        self._fps_dirty_rect = None
        self.show_framerate = False
        if switch_resolution:
            self._surface = None
        # initialize pygame in case it's not already
        try:
            self._update_screen()
        except pygame.error:
            pygame.init()
            self._update_screen()
        # in fullscreen mode: save all available modes for the settings
        self._display_modes = None
        self._check_display_modes()
        # set the window title
        self.caption = caption

    def run(self):
        """Thread main run function

        Overrides: threading.Thread.run()
        """
        # run_counter = 0
        # refresh_time = self.fps * 10
        fps_counter = 0
        fps_interval = self.fps

        while self.thread_is_running:
            '''this might provoke screen flickering
            if refresh_time <= run_counter:
                # completely refresh screen once every 10 seconds
                self.refresh_screen(True)
                run_counter = 0
            else:
            '''
            # only update screen parts that changed
            if self._rects_to_update:
                self.refresh_screen()
            #   run_counter += 1

            if self.show_framerate:
                if fps_counter >= fps_interval:
                    self._render_current_fps()
                    fps_counter = 0
                else:
                    fps_counter += 1
            self.clock.tick(self.fps)

    def _update_screen(self):
        """switch to windowed or fullscreen mode"""
        display = pygame.display.Info()

        if self.fullscreen:
            pygame.mouse.set_visible(False)
            '''if switch resolution is False, render to a smaller surface but show it centered on the full screen'''
            if not self.switch_resolution:
                self._screen = pygame.display.set_mode((display.current_w, display.current_h), FULLSCREEN, display.bitsize)
                self._surface = pygame.Surface((self._screen_x, self._screen_y))
                self.blit(self._surface, None, True)
            else:
                '''switch screen resolution to the desired one'''
                self._screen = pygame.display.set_mode((self._screen_x, self._screen_y), FULLSCREEN, display.bitsize)
        else:
            pygame.mouse.set_visible(True)
            self._screen = pygame.display.set_mode((self._screen_x, self._screen_y), 0, display.bitsize)    # RESIZABLE

        self.refresh_screen(True)

    def refresh_screen(self, complete_screen=False):
        """refresh the pygame screen/window"""
        if not self.rects_to_update and not complete_screen:
            print(str("nothing to udpate, refreshing the whole screen; use refresh_screen(True) to avoid this message"))
            complete_screen = True

        '''frame rate persistence'''
        if self.show_framerate:
            self._show_fps_blit()

        try:
            # redraw the whole screen
            if complete_screen and not self._force_refresh:
                # lock the screen update process
                self._force_refresh = True
                # clear the rects to update list
                self._rects_to_update = []
                # and update the whole screen
                pygame.display.update()
                self._force_refresh = False
            else:
                # only update the changed rects
                try:
                    if not self._updating_screen:
                        # only one function call is allowed to update the screen at once
                        self._updating_screen = True
                        '''force refresh has priority to avoid flickering
                           by not allowing multiple display updates ot once'''
                        while self.rects_to_update and not self._force_refresh:
                            pygame.display.update(self.rects_to_update.pop())
                        self._updating_screen = False
                except ValueError or pygame.error:
                    '''completely refresh the screen'''
                    print("Error occured parsing " + str(self._rects_to_update))
                    self._rects_to_update = []
                    self.refresh_screen()
        except pygame.error:
            # OpenGL can only redraw the whole screen
            try:
                pygame.display.flip()
            except pygame.error:
                self.refresh_screen(True)

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

        # TODO: fix background misplacement if the window get's manually resized
        # if self.bg_surface.get_width() is not self._screen_x or self.bg_surface.get_height() is not self._screen_y:
        #    '''redraw the background'''
        #    self.bg_surface = pygame.transform.scale(self.bg_surface, (self._screen_x, self._screen_y))
        #    self._fps_dirty_rect = None
        #    self.blit(self.bg_surface, (0, 0))

        # update the screen
        self._update_screen()

    def _render_current_fps(self):
        """draws the current frame rate in the screens up right corner"""
        width = self.screen.get_width()
        pos_x = width - 60
        pos_y = 30
        font = pygame.font.Font(None, 24)
        text = '%.2f' % self.clock.get_fps()
        font_rendered = font.render(text, True, WHITE, SRCALPHA)
        font_rect = font_rendered.get_rect()
        if not self._fps_dirty_rect and self.bg_surface:
            '''get the clean background rect with some additional security padding around it'''
            try:
                self._fps_dirty_rect = self.bg_surface.subsurface(
                    (pos_x - 5, pos_y - 5, font_rect.width + 10, font_rect.height + 10))
            except ValueError:
                '''if the subsurface bounces out of the main surface disable fps to avoid a render thread crash'''
                self.show_framerate = False

        self._fps_surface = (font_rendered, (pos_x, pos_y))
        # blit it to the screen
        self._show_fps_blit()

    def _show_fps_blit(self):
        """adds the ability to keep the last calculated fps value on top on a screen refresh"""
        if self._fps_dirty_rect and self._fps_surface:
            surf, pos = self._fps_surface
            pos_x, pos_y = pos
            self.blit(self._fps_dirty_rect, (pos_x - 5, pos_y - 5))
            self.blit(surf, pos)
            # update the dirty rect area because it's a little bit bigger
            self.add_rect_to_update(self._fps_dirty_rect.get_rect(), surf, pos, False)

    @property
    def caption(self):
        """ Title of the pygame window

        Returns: caption (str)
        """
        return self._caption

    @caption.setter
    def caption(self, caption):
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

    def add_rect_to_update(self, rects, surface=None, pos=None, centered=None):
        """Add a rect or list of rects at the beginning of the rects_to_update list.
           This is to ensure the FIFO principle because the rendering function always
           pops the last item out of the list.

           This function automatically corrects offsets between the drawing surface
           and the screen if a surface is provided.

           Providing a surface additionally requires either a pos or centered=True value.

        Args:
            rects (pygame.Rect or [pygame.Rect]): Rect or List of Rects to add
            surface (pygame.Surface): the area the rect is drawn to
            pos (int, int): the offset of that surface on the screen (obsolete if centered is True)
            centered (bool): if the surface is centered on the screen or not (pos required if False)
        """
        def add_rect(single_rect):
            # make sure not to add something wrong because pygame.display.update is very sensible
            if type(single_rect) is pygame.Rect:
                self._rects_to_update.insert(0, single_rect)
            else:
                print(str(single_rect) + " is no valid pygame.Rect")

        if surface:
            rects = self._fix_update_rects(rects, surface, pos, centered)

        if type(rects) is list:
            for i in range(0, len(rects)):
                # add the list one by one because pygame.display.update()
                # doesn't allow multi dimensional lists
                add_rect(rects[i])
        else:
            add_rect(rects)

    def _offsets_for_centered_surface(self, surface, pos, centered):
        """This function calculates the offsets to center smaller surfaces on the main screen
           and to determine the offsets to pass the correct rects to pygame.display.update().
           This is mainly important because MacOS X takes the smaller surface offset into account
           (or it might quietly update the whole screen) while Linux doesn't refresh anything
           because the rects are misplaced)

        Args:
            surface (pygame.Surface): the surface that's drawn to the screen
            pos (int, int): the position where it should be drawn
            centered (bool): determines if the surface should be/is centered on the screen

        Returns: (int, int) as x and y offset
        """
        if centered:
            s_width = surface.get_width()
            s_height = surface.get_height()
            scr_width = self.screen.get_width()
            scr_height = self.screen.get_height()
            if s_width is not scr_width and s_height is not scr_height:
                offset_x = s_width - scr_width if s_width > scr_width else scr_width - s_width
                offset_y = s_height - scr_height if s_height > scr_height else scr_height - s_height
                offset_x //= 2
                offset_y //= 2
                pos = (offset_x, offset_y)
            else:
                '''same size'''
                pos = (0, 0)

        if not self.switch_resolution and self.fullscreen:
            '''calculate offset if rendering surface is smaller than the screen size'''
            margin_x, margin_y = pos
            margin_x += (self._screen.get_width() - self._surface.get_width()) // 2
            margin_y += (self._screen.get_height() - self._surface.get_height()) // 2
            pos = (margin_x, margin_y)

        return pos

    def _fix_update_rects(self, rects, surface, pos, centered):
        """calculate the correct rects to update and add a small margin

        Args:
            surface (pygame.Surface): the smaller surface that was rendered to
            pos (int, int) or None: the position the surface was placed
            centered: if the surface is centered on screen (ignores pos)
            rects: the rects that changed on the smaller surface

        Returns: list(pygame.Rect) with all altered rects
        """
        def fix_rect():
            m_dim = 4  # 2 pixels wider in each direction
            m_pos = m_dim // 2
            diff_x, diff_y = self._offsets_for_centered_surface(surface, pos, centered)
            rect = pygame.Rect(x + diff_x - m_pos, y + diff_y - m_pos, width + m_dim, height + m_dim)
            rects_fixed.append(rect)

        rects_fixed = []
        rect_type = type(rects)

        if rect_type is list:
            while rects:
                x, y, width, height = rects.pop()
                fix_rect()
        elif rect_type is pygame.Rect:
            x, y, width, height = rects
            fix_rect()

        '''pass the changed rects to the render thread / pygame'''
        return rects_fixed

    def blit(self, surface, pos, center=False):
        """blit a surface to the main screen

        Args:
            surface (pygame.Surface): surface to draw to the screen
            pos (int x, int y): position where to draw it at the screen (also accepts a Rect)
            center (bool): if set pos get's ignored and the surface is centered on the screen
        """
        pos = self._offsets_for_centered_surface(surface, pos, center)
        rect = surface.get_rect()
        rect.x, rect.y = pos
        self._screen.blit(surface, rect)

    def stop_thread(self):
        """stop the current thread by disabling its run loop"""
        self.thread_is_running = False

    @property
    def screen(self):
        """return the main drawing surface

        Returns: pygame.Surface
                the whole screen if switch_resolution is set or else
                a smaller,centered surface with the requested dimensions
        """
        if not self.fullscreen or self.switch_resolution:
            return self._screen
        else:
            return self._surface

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
            self._update_screen()

    def _check_display_modes(self):
        """store all available display modes in fullscreen

        Cave: should only be run once on (full)screen initialization because it causes heavy flickering
        """
        self._display_modes = pygame.display.list_modes()

    @property
    def display_modes(self):
        """return the saved list of display modes

        Returns: display_modes ([(x, y)]): tuples of width and heights in a list
        """
        return self._display_modes

