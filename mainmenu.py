import pygame
from pygame.locals import *
'''
Main Menu
    - Start New Game
        - Singleplayer
            - New Game              -> start_game()
            - Resume                -> ?
            - Difficulty            -> options_difficulty() -> left/right switch easy medium hard
        - Multiplayer
            - cooperative
                - Local             -> start_coop_local()
                - LAN               -> start_coop_lan()
            - versus
                - LAN               -> start_versus()
    - Settings
        - Video
            - Resolution        -> pygame.display.list_modes() as list left/right switchable
            - Fullscreen        -> on/off
            - Upscaling         -> on/off
            - FPS               -> ?
        - Audio                 -> ?
            - Music             -> on/off
            - Music Volume      -> options_volume_music()   -> bar 0 - 100% -> grayed out if off
            - Effects Volume    -> options_volume_fx()      -> bar 0 - 100%
        - Controls
            - Key Mapping       -> options_controls_keys()
                - Left
                - Right
                - Up
                - Down
                - Jump          -> ?
                - Shoot
                - Interact      -> ?
            - Gamepad           -> options_controls_gamepad()
                - same as keys
        - Reset Settings        -> ask(yes/no) -> options_config_reset() -> settings.write_settings(True)
    - Exit
'''

'''Constants'''
BLACK = pygame.Color(0, 0, 0)
GRAY = pygame.Color(150, 150, 150)
WHITE = pygame.Color(255, 255, 255)
RED = pygame.Color(150, 0, 0)
MENU_FONT = "./resources/fonts/Mikodacs.otf"
BACKGROUND = pygame.Color(100, 100, 100)
# including 2 for the header
MAX_ITEMS_NO_SCROLL = 7
# space between two entries
LINE_SPACING = 1.5


class Menu(object):
    """Menu class which contains several MenuItems

    Args:
        surface (pygame.Surface): the surface the menu get's drawn to
        parent (Menu):  parent menu if this is a sub-menu
        font_size (int): size which is used for the "Back" Button if it's a sub menu
    """

    def __init__(self, surface, render_thread, parent=None, font_size=36):
        self.surface = surface
        self.render_thread = render_thread
        # self.surface.set_alpha(0)
        self.parent = parent
        self.font_size = font_size
        self.menu_items = []
        self.length = 0
        self.background = None
        if self.parent:
            # always add a back button for sub-menus
            self.add_menu_item(MenuItem("Back", self.parent, self.font_size))
        # initialize the pygame font rendering engine
        pygame.font.init()

    def add_menu_item(self, menu_item):
        """add a new MenuItem to this Menu

        Args:
            menu_item (MenuItem): the new MenuItem to add to the list of menu-items
        """
        if self.parent:
            # keep the back button at the end of the menu items list
            self.menu_items.insert(self.length - 1, menu_item)
        else:
            self.menu_items.append(menu_item)
        # finish MenuItem initialization / make the MenuItem aware to which Menu it belongs
        menu_item.menu = self
        # keep track of the menu size
        self.length += 1

    def get_menu_item(self, index):
        """Return the MenuItem at a specific index

        Args:
            index (int): index of the requested MenuItem

        Returns: MenuItem
        """
        return self.menu_items[index]

    def draw_item(self, menu_item, index, pos, margin_top=None):
        """draw a specific MenuItem

        Args:
            menu_item (MenuItem): MenuItem to draw
            index (int): position of the MenuItem in the Menu used to highlight the first item
            pos (int): position of the currently selected item in the Menu used to highlight the selected item
            margin_top (int): vertical position where this item will be rendered

        Returns: pygame.Rect
        """
        menu_item.rect.centerx = self.surface.get_rect().centerx
        if margin_top:
            menu_item.rect.centery = margin_top
        menu_item.hovered = True if index is 0 or index is pos else False
        # overwrite the old rendering
        pygame.draw.rect(self.surface, BACKGROUND, menu_item.get_rect())
        # draw the new rendering
        menu_item.draw()

        return menu_item.get_rect()

    def print_menu(self, new_pos=1, old_pos=1, complete=True, start_pos=1):
        """Print the whole menu or individual menu items

        Args:
            new_pos (int): user selected menu item
            old_pos (int): previous selected menu item
            complete (bool): render the whole menu
            start_pos (int): offset at which to start rendering the menu (scrolling)

        Returns: list(pygame.Rect) for pygame to update the screen parts
        """
        length = self.length
        arrow_pos_x = self.surface.get_width() - self.font_size * 2.25
        arrow_pos_y = self.surface.get_height() - self.font_size * 2
        rects = []
        max_items_view = MAX_ITEMS_NO_SCROLL - 2  # including 2 for the header
        stop_pos = start_pos + max_items_view if start_pos + max_items_view < length else length

        # limit the cursor
        if new_pos is length:
            new_pos = length - 1

        margin_top = self.menu_items[0].size

        if complete:
            # draw the fancy background
            rects.append(self.draw_background(BACKGROUND))
            # always draw the first item (header)
            rects.append(self.draw_item(self.menu_items[0], 0, new_pos, margin_top))
            margin_top += self.menu_items[1].size

            for menu_index in range(start_pos, stop_pos):
                menu_item = self.menu_items[menu_index]
                margin_top += menu_item.size * LINE_SPACING
                rects.append(self.draw_item(self.menu_items[menu_index], menu_index, new_pos, margin_top))

            '''draw arrows if the menu is too long to notify about that'''
            if length > MAX_ITEMS_NO_SCROLL:
                if start_pos is not 1:
                    # up facing arrow
                    rects.append(self.draw_arrow(arrow_pos_x, self.font_size * 2, self.font_size, False))
                if stop_pos is not length:
                    # down facing arrow
                    rects.append(self.draw_arrow(arrow_pos_x, arrow_pos_y - self.font_size, self.font_size))
        else:
            '''partial screen update'''
            new_option = self.menu_items[new_pos]
            old_option = self.menu_items[old_pos]

            if length > MAX_ITEMS_NO_SCROLL:
                if new_pos < old_pos:
                    # if the cursor moves up
                    if new_pos % max_items_view is 0:
                        # scroll page wise up if the next item is out of sight
                        return self.print_menu(new_pos, old_pos, True, old_pos - max_items_view)
                else:
                    # if the cursor moves down
                    if old_pos % max_items_view is 0:
                        # scroll page wise down if the next item is out of sight
                        return self.print_menu(new_pos, old_pos, True, new_pos)

            # update the changed items
            rects.append(self.draw_item(new_option, new_pos, new_pos))
            rects.append(self.draw_item(old_option, old_pos, new_pos))
        '''bug fix for fucking linux not taking into account that the smaller surface is centered on the bigger one'''
        rects_fix = []
        diff_x = int((self.render_thread.screen.get_width() - self.surface.get_width()) / 2)
        diff_y = int((self.render_thread.screen.get_height() - self.surface.get_height()) / 2)
        while rects:
            x, y, width, height = rects.pop()
            rect = pygame.Rect(x + diff_x, y + diff_y, width, height)
            rects_fix.append(rect)
        '''pass the changed rects to the render thread / pygame'''
        return rects_fix

    def draw_background(self, bgcolor):
        """draws a custom shaped background to the main surface"""
        if not self.background:
            '''only draw it once'''
            width = self.surface.get_width()
            height = self.surface.get_height()
            bg_surface = pygame.Surface((width, height), SRCALPHA)
            radius = 20
            width -= radius
            height -= radius

            background_rect = pygame.Rect(10, 10, width, height)
            background_rect.union_ip(pygame.draw.rect(bg_surface, bgcolor, background_rect, 0))
            background_rect.union_ip(pygame.draw.rect(bg_surface, RED, background_rect, 5))
            background_rect.union_ip(pygame.draw.circle(bg_surface, RED, (radius, radius), radius))
            background_rect.union_ip(pygame.draw.circle(bg_surface, RED, (width, radius), radius))
            background_rect.union_ip(pygame.draw.circle(bg_surface, RED, (radius, height), radius))
            background_rect.union_ip(pygame.draw.circle(bg_surface, RED, (width, height), radius))
            '''and save the result for later use'''
            self.background = bg_surface

        self.surface.blit(self.background, (0, 0))

        return self.background.get_rect()

    def calc_font_size(self, header_size, font_size):
        """calculate a ratio to multiply font sizes with to adjust them for different screen sizes

        Cave: this should be called right after creating the top level menu BEFORE creating any MenuItem
              MenuItems need to be initialized with the correct font size else many things tend to break!

        Args:
            header_size (int): font size used for the first Menu entry e.g. the header
            font_size (int): font size used for all other entries

        Returns: ratio to multiply your favored font sizes with, which then can be passed to MenuItems and sub menus
        """
        height = self.surface.get_height()
        width = self.surface.get_width()
        size = height if height < width else width
        text_space = font_size * LINE_SPACING * MAX_ITEMS_NO_SCROLL
        ratio = round((size - header_size) / text_space, 2)

        return ratio

    def draw_arrow(self, pos_x, pos_y, size, down=True, color=GRAY):
        """draw an up or down facing arrow used to indicate scrolling capabilities

        Args:
            pos_x (int): the arrows horizontal position
            pos_y (int): the arrows vertical position
            size (int): draws the arrow in this size in pixels (e.g. font size)
            down (bool): downward facing arrow if true, upwards if false
            color (Pygame.Color): the color of the arrow

        Returns: pygame.Rect
        """
        width = size / 3
        height = size / 2
        arrow_botm_x = pos_x + width + height
        arr_down_y = pos_y
        arr_down_tip_y = pos_y + height + height
        if not down:
            arr_down_y += height
            arr_down_tip_y = pos_y
        arrow_bottom = pygame.Rect(arrow_botm_x, arr_down_y, width, height)
        arrow_h_p1 = (arrow_botm_x - size / 5 - 1, pos_y + height)  # compensate int rounding
        arrow_h_p2 = (arrow_botm_x + width + size / 5, pos_y + height)
        arrow_h_p3 = (arrow_botm_x + width / 2 - 1, arr_down_tip_y)  # compensate int rounding

        arrow_base = pygame.draw.rect(self.surface, color, arrow_bottom, 0)
        tip = pygame.draw.polygon(self.surface, color, (arrow_h_p1, arrow_h_p2, arrow_h_p3), 0)

        arrow_base.union_ip(tip)

        '''return the complete arrow'''
        return arrow_base


class MenuItem(object):
    """ Individual MenuItem stored in a Menu

    Args:
        text (str): Menu item text
        action (Menu or function): action to execute or menu to switch to when item get's selected
        size (int): text size for the Menu item text
    """
    hovered = False

    def __init__(self, text, action, size=36):
        self.menu = None
        self.text = text
        self.action = action
        self._size = size
        # initialize the font renderings
        self.font = pygame.font.Font(MENU_FONT, size)
        self.font_renderer = None
        self.rect = None
        self.set_rect()

    def draw(self):
        """(re)draw this item"""
        self.set_renderer()
        self.menu.surface.blit(self.font_renderer, self.rect)

    def get_rect(self):
        """returns the rendered pygame.Rect

        Returns: pygame.Rect
        """
        return self.rect

    def set_renderer(self):
        """set the font renderer"""
        self.font_renderer = self.font.render(self.text, True, self.get_color())

    def get_color(self):
        """get the current Color of this Item

        Returns: RGB tuple: white if hovered, red else
        """
        if self.hovered:
            return (255, 255, 255)
        else:
            return (100, 0, 0)

    def set_rect(self):
        """draw the pygame.Rect containing this menu item"""
        self.set_renderer()
        self.rect = self.font_renderer.get_rect()

    def get_action(self):
        """get the action or sub-menu stored in this menu item

        Returns: Menu or function to be executed after parsing it with eval()
        """
        return self.action

    @property
    def size(self):
        """changing the size only works when reinitializing the whole MenuItem that's why it's read only

        Returns: text size of this menu item (int)
        """
        return self._size
