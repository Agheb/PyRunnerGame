#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Menu and MenuItem class to create a new (Sub)Menu"""

# universal imports
import textwrap

from pyrunner_classes import *

'''constants'''
# including 2 for the header
MAX_ITEMS_NO_SCROLL = 7
# space between two entries
LINE_SPACING = 1.5


class Menu(object):
    """Create a new (Sub)Menu

    Args:
        init (class): the class calling this to use the set_current_menu function for the back item
        name (str): name of this Menu
        surface (pygame.Surface): the surface this menu is drawn to
        parent (Menu or None): the parent menu if existent
        font_size (int, int, int): font size for all items (header 1, 2 and text)
    """

    def __init__(self, init, name, surface, parent=None, font_size=(72, 48, 36)):
        self.init = init
        self.name = name
        self.surface = surface
        self.width = surface.get_width()
        self.height = surface.get_height()
        self.parent = parent
        self.font_h1_size, self.font_h2_size, self.font_text_size = font_size
        self.font_size = font_size
        self.menu_items = []
        self.sub_menus = []
        self.length = 0
        self.background = None
        self.error_menu = None
        '''init the basic menu structure'''
        self.add_structure()

        # initialize the pygame font rendering engine
        pygame.font.init()

    def add_submenu(self, name, hidden=False):
        """add a sub menu to this menu"""
        submenu = Menu(self.init, name, self.surface, self, self.font_size)
        self.sub_menus.append(submenu)
        if not hidden:
            self.add_item(MenuItem(name, self.init.set_current_menu, vars=submenu))
        return submenu

    def add_structure(self):
        """add heading and back button"""
        if self.parent:
            # always add a back button for sub-menus
            self.add_item(MenuItem("Back", self.init.set_current_menu, vars=self.parent))
        # add the name as first menu item (saves another font render routine)
        self.add_item(MenuItem(self.name))

    def add_item(self, menu_item):
        """add a new MenuItem to this Menu

        Args:
            menu_item (MenuItem): the new MenuItem to add to the list of menu-items
        """
        # finish MenuItem initialization / make the MenuItem aware to which Menu it belongs
        if self.length is 0 and not self.parent:
            menu_item.size = self.font_h1_size
        elif self.length is 1 and self.parent:
            menu_item.size = self.font_h2_size
        else:
            menu_item.size = self.font_text_size
        menu_item.menu = self
        menu_item.finish_init()

        if self.parent:
            # keep the back button at the end of the menu items list
            self.menu_items.insert(self.length - 1, menu_item)
        else:
            self.menu_items.append(menu_item)
        # keep track of the menu size
        self.length += 1

    def get_item(self, index):
        """Return the MenuItem at a specific index

        Args:
            index (int): index of the requested MenuItem

        Returns: MenuItem
        """
        return self.menu_items[index]

    def delete_item(self, name):
        """remove a menu item"""
        for item in self.menu_items:
            if item.name == name or item.id == name:
                self.length -= 1
                return self.menu_items.remove(item)

    def flush_all_items(self):
        """remove all items except for the header and back button"""
        self.menu_items = []
        self.length = 0

        self.add_structure()

    def print_error(self, error_string):
        """show errors in the menu"""
        '''split longer text into multiple items'''
        len_per_line = 30

        if len(error_string) > len_per_line * 4:
            return print(error_string)

        if self.error_menu:
            error_string = textwrap.wrap(error_string, len_per_line, break_long_words=False)

            self.error_menu.flush_all_items()

            for text in error_string:
                self.error_menu.add_item(MenuItem(text, None))
            '''show the new Menu on the screen'''
            self.init.set_current_menu(self.error_menu)
            self.init.show_menu(True)
        else:
            self.error_menu = self.add_submenu("Error", True)
            self.print_error(error_string)

    def _draw_item(self, menu_item, index, pos, margin_top=None):
        """draw a specific MenuItem

        Args:
            menu_item (MenuItem): MenuItem to draw
            index (int): position of the MenuItem in the Menu used to highlight the first item
            pos (int): position of the currently selected item in the Menu used to highlight the selected item
            margin_top (int): vertical position where this item will be rendered

        Returns: pygame.Rect
        """
        menu_item.rect.centerx = self.surface.get_rect().centerx
        old_rect = None
        # if margin_top:
        #    menu_item.rect.centery = margin_top
        menu_item.hovered = True if (index is 0 or index is pos) and menu_item.action else False
        if menu_item.prev_rect:
            if not margin_top:
                margin_top = menu_item.prev_rect.top
            '''clear the old rendering'''
            old_rect = self._clear_rect(menu_item.prev_rect, margin_top)

        '''and clear the new rect'''
        self._clear_rect(menu_item.get_rect(), margin_top)
        # draw the new rendering
        new_rect = menu_item.draw(margin_top)

        if not old_rect:
            old_rect = new_rect

        return new_rect if new_rect.contains(old_rect) else old_rect

    def _clear_rect(self, rect, margin_top):
        """clear a menu item rect"""
        rect.top = margin_top
        rect.centerx = self.surface.get_rect().centerx
        return pygame.draw.rect(self.surface, BACKGROUND, rect)

    def print_menu(self, new_pos=1, old_pos=1, complete=True, start_pos=1, rects=list()):
        """Print the whole menu or individual menu items

        Args:
            new_pos (int): user selected menu item
            old_pos (int): previous selected menu item
            complete (bool): render the whole menu
            start_pos (int): offset at which to start rendering the menu (scrolling)
            rects (list): rects if the menu already partially changed before calling this function

        Returns: list(pygame.Rect) for pygame to update the screen parts
        """
        length = self.length
        rects = rects
        max_items_view = MAX_ITEMS_NO_SCROLL - 2  # including 2 for the header

        # limit the cursor - is done in pyRunner.py
        # if new_pos is length:
        #    new_pos = length - 1

        if complete:
            stop_pos = start_pos + max_items_view if start_pos + max_items_view < length else length
            # draw the fancy background
            rects.append(self._draw_background(BACKGROUND))
            # don't overwrite the header
            margin_top = self.font_h1_size + 4
            # always draw the first item (header)
            rects.append(self._draw_item(self.menu_items[0], 0, new_pos, margin_top))
            margin_top += self.font_text_size

            '''draw all menu items that are in the current view'''
            for index, item in enumerate(self.menu_items[start_pos:stop_pos], start_pos):
                margin_top += item.size * LINE_SPACING
                rects.append(self._draw_item(item, index, new_pos, margin_top))

            '''draw arrows if the menu is too long to notify about that'''
            if length > MAX_ITEMS_NO_SCROLL:
                # arrow positions
                font_size = self.font_text_size
                size_2 = font_size + font_size  # faster then * 2
                arrow_pos_x = int(self.width - font_size * 2.25)
                arrow_pos_y = self.height - size_2

                if start_pos is not 1:
                    # up facing arrow
                    rects.append(self._draw_arrow(arrow_pos_x, size_2, font_size, False))
                if stop_pos is not length:
                    # down facing arrow
                    rects.append(self._draw_arrow(arrow_pos_x, arrow_pos_y - font_size, font_size))
        else:
            '''partial screen update'''
            new_option = self.menu_items[new_pos]
            old_option = self.menu_items[old_pos]

            if length > MAX_ITEMS_NO_SCROLL and not new_pos == old_pos:
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
            rects.append(self._draw_item(new_option, new_pos, new_pos))
            rects.append(self._draw_item(old_option, old_pos, new_pos))

        if not self.menu_items[new_pos].action:
            changed_pos = new_pos + 1 if old_pos <= new_pos else new_pos - 1
            new_old_pos = old_pos + 1 if old_pos <= new_pos else old_pos - 1
            return self.print_menu(changed_pos, new_old_pos, False, start_pos, rects)
        '''bug fix the rects positions and pass the changed rects to the render thread / pygame'''
        return rects, new_pos

    def _draw_background(self, bg_color):
        """draws a custom shaped background to the main surface"""
        if not self.background:
            '''only draw it once'''
            width = self.width
            height = self.height
            '''corner rect position and size'''
            # size = 24
            # pos_right = width - size
            # pos_bottom = height - size
            bg_surface = pygame.Surface((width, height))

            background_rect = pygame.Rect(0, 0, width, height)
            background_rect.union_ip(pygame.draw.rect(bg_surface, bg_color, background_rect))
            background_rect.union_ip(pygame.draw.rect(bg_surface, GRAY, background_rect, 8))
            # background_rect.union_ip(pygame.draw.rect(bg_surface, GRAY, (0, 0, size, size)))
            # background_rect.union_ip(pygame.draw.rect(bg_surface, GRAY, (pos_right, 0, size, size)))
            # background_rect.union_ip(pygame.draw.rect(bg_surface, GRAY, (0, pos_bottom, size, size)))
            # background_rect.union_ip(pygame.draw.rect(bg_surface, GRAY, (pos_right, pos_bottom, size, size)))
            '''and save the result for later use'''
            self.background = bg_surface

        self.surface.blit(self.background, (0, 0))

        return self.background.get_rect()

    @staticmethod
    def calc_font_size(surface, header_size, font_size):
        """calculate a ratio to multiply font sizes with to adjust them for different screen sizes

        Cave: this should be called right after creating the top level menu BEFORE creating any MenuItem
              MenuItems need to be initialized with the correct font size else many things tend to break!

        Args:
            surface (pygame.Surface): the surface the menu is drawn to
            header_size (int): font size used for the first Menu entry e.g. the header
            font_size (int): font size used for all other entries

        Returns: ratio to multiply your favored font sizes with, which then can be passed to MenuItems and sub menus
        """
        width = surface.get_width()
        height = surface.get_height()
        size = height if height < width else width
        text_space = font_size * LINE_SPACING * MAX_ITEMS_NO_SCROLL
        ratio = round((size - header_size) / text_space, 2)

        return ratio

    def _draw_arrow(self, pos_x, pos_y, size, down=True, arrow_color=GRAY):
        """draw an up or down facing arrow used to indicate scrolling capabilities

        Args:
            pos_x (int): the arrows horizontal position
            pos_y (int): the arrows vertical position
            size (int): draws the arrow in this size in pixels (e.g. font size)
            down (bool): downward facing arrow if true, upwards if false
            arrow_color (Pygame.Color): the color of the arrow

        Returns: pygame.Rect
        """
        width = size // 3
        height = size // 2
        arrow_botm_x = pos_x + width + height
        arr_down_y = pos_y
        arr_down_tip_y = pos_y + height + height
        if not down:
            arr_down_y += height
            arr_down_tip_y = pos_y
        arrow_bottom = pygame.Rect(arrow_botm_x, arr_down_y, width, height)
        arrow_h_p1 = (arrow_botm_x - size // 5 - 1, pos_y + height)  # compensate int rounding
        arrow_h_p2 = (arrow_botm_x + width + size // 5, pos_y + height)
        arrow_h_p3 = (arrow_botm_x + width // 2 - 1, arr_down_tip_y)  # compensate int rounding

        arrow_base = pygame.draw.rect(self.surface, arrow_color, arrow_bottom)
        tip = pygame.draw.polygon(self.surface, arrow_color, (arrow_h_p1, arrow_h_p2, arrow_h_p3))
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

    def __init__(self, name, action=None, **kwargs):
        self.menu = None
        self._name = name
        self.id = None
        self.size = None
        self.action = action
        self._action_values = None
        self.font = None
        self.font_renderer = None
        self.rect = None
        self._val = None
        self.bar = None
        self.prev_rect = None

        # parse additional values
        for name, value in kwargs.items():
            if name == "vars":
                self._action_values = value
            elif name == "val":
                self._val = value
            elif name == "bar":
                self.bar = value

    def finish_init(self):
        """finish initialization after an item has been added to a Menu"""
        # initialize the font renderings
        self.font = pygame.font.Font(MENU_FONT, self.size)
        self.set_rect()

    def do_action(self):
        """execute passed function"""
        try:
            try:
                self.action(self._action_values)
            except TypeError:
                self.action()
        except TypeError as e:
            '''if the action is invalid/uninitialized just ignore it'''
            print("invalid action %s in %s/%s [%s]" % (self.action, self.menu.name, self._name, e))
            pass

    def draw(self, margin_top=None):
        """(re)draw this item"""
        self.set_renderer()
        if margin_top:
            self.rect.top = margin_top
        self.menu.surface.blit(self.font_renderer, self.rect)

        return self.rect

    def get_rect(self):
        """returns the rendered pygame.Rect

        Returns: pygame.Rect
        """
        return self.rect

    def set_renderer(self):
        """set the font renderer"""
        self.prev_rect = self.rect if self.rect else None
        self.font_renderer = self.font.render(self.text, True, self.get_color())

    @property
    def text(self):
        """get a full menu item text representation"""
        if self._val is not None:
            if self.bar is not None:
                '''music/sound volume bars'''
                return '{:<14s} {:<5s} {:10s}'.format(self._name, self.bool_to_string(self._val),
                                                      self.print_bar(self.bar))

            if isinstance(self._val, str):
                return '{:<10s}: {:>20s}'.format(self._name, self._val)
            elif self._val > 1 and isinstance(self._val, int):
                '''key setups'''
                return '{:>16s}  :  {:<16s}'.format(self._name, pygame.key.name(self._val))
            else:
                '''music/sound on/off etc'''
                return '{:<28s} {:>6s}'.format(self._name, self.bool_to_string(self._val))
        else:
            return self._name

    @property
    def name(self):
        """return the item text name"""
        return self._name

    @name.setter
    def name(self, new_name):
        """change the item name and rerender the font"""
        self._name = new_name
        self.set_rect()

    @property
    def val(self):
        """return the current item value"""
        return self._val

    @val.setter
    def val(self, new_val):
        """set the value to a new value"""
        self._val = new_val
        self.set_rect()

    def get_color(self):
        """get the current Color of this Item

        Returns: RGB tuple: white if hovered, red else
        """
        if self.hovered:
            return WHITE
        else:
            return GRAY

    def set_rect(self):
        """draw the pygame.Rect containing this menu item"""
        self.set_renderer()
        self.rect = self.font_renderer.get_rect()

    def get_action(self):
        """get the action or sub-menu stored in this menu item

        Returns: Menu or function to be executed after parsing it with eval()
        """
        return self.action

    def size(self):
        """changing the size only works when reinitializing the whole MenuItem that's why it's read only

        Returns: text size of this menu item (int)
        """
        return self.size

    @staticmethod
    def print_bar(val):
        """ a little helper function to visualize the volume level of a specific channel
        Args:
            val (int): value from 0 to 10 which get's filled according to the volume level

        Returns: a 10 character long string representing the volume bar
        """
        return "".join(["|" if i is val else "-" for i in range(11)])

    @staticmethod
    def bool_to_string(boolean):
        """helper function for the MenuItems containing booleans in their name"""
        return "on" if boolean else "off"
