import pygame
"""

    Main Menu
        - Start New Game
            - Singleplayer
                - New Game              -> start_game()
                - Resume                -> ?
                - Difficulty            -> options_difficulty() -> left/right switch easy medium hard

                - Back/Previous
            - Multiplayer
                - cooperative
                    - Local             -> start_coop_local()
                    - LAN               -> start_coop_lan()

                    - Back/Previous
                - versus
                    - LAN               -> start_versus()

                    - Back/Previous

                - Back/Previous
            - Settings
                - Video
                    - Resolution        -> pygame.display.list_modes() as list left/right switchable
                    - Aspect-Ratio      -> ?
                    - Fullscreen        -> on/off
                    - Upscaling         -> on/off
                    - FPS               -> ?

                    - Back/Previous
                - Audio
                    - Music             -> on/off
                    - Music Volume      -> options_volume_music()   -> bar 0 - 100% -> grayed out if off
                    - Effects Volume    -> options_volume_fx()      -> bar 0 - 100%

                    - Back/Previous
                - Controls
                    - Key Mapping       -> options_controls_keys()
                        - Left
                        - Right
                        - Up
                        - Down
                        - Jump          -> ?
                        - Shoot
                        - Interact      -> ?

                        - Back/Previous
                    - Gamepad           -> options_controls_gamepad()
                        - same as keys

                        - Back/Previous
                - Reset Settings        -> ask(yes/no) -> options_config_reset() -> settings.write_settings(True)

                - Back/Previous

        - Exit

"""

"""Constants"""
BLACK = pygame.Color(0, 0, 0)
MENU_FONT = "./resources/fonts/Mikodacs.otf"
BACKGROUND = pygame.Color(200, 200, 200)


class Menu(object):
    """Menu class which contains several MenuItems

        Args:
            surface: the surface the menu get's drawn to
    :type surface:  pygame.Surface
    :param parent:  parent menu if this is a sub-menu
    :type parent:   Menu
    """

    def __init__(self, surface, parent=None):
        self.surface = surface
        self.parent = parent
        self.menu_items = []
        self.length = 0
        if self.parent:
            # always add a back button for sub-menus
            self.add_menu_item(MenuItem("Back", self.parent))
        # initialize the pygame font rendering engine
        pygame.font.init()

    def add_menu_item(self, menu_item):
        """Menu class which contains several MenuItems

        :param menu_item: the new MenuItem to add to the list of menu-items
        :type menu_item: MenuItem
        """
        if self.parent:
            # keep the back button at the end of the menu items list
            self.menu_items.insert(self.length - 1, menu_item)
        else:
            self.menu_items.append(menu_item)
        # finish MenuItem initialization / make the MenuItem aware to which Menu it belongs
        menu_item.set_menu(self)
        self.length += 1

    def get_menu_item(self, index):
        """Return the MenuItem at a specific index

        :param index: index of the requested MenuItem
        :type index: int
        :return: MenuItem
        """
        return self.menu_items[index]

    def get_surface(self):
        """Return the surface this Menu is drawn to

            Returns:
                surface (Pygame.surface): surface this Menu is drawn to
        """
        return self.surface

    def set_surface(self, surface):
        """Set the surface to which this Menu will be drawn

        :param surface: the new surface which will be used for all drawings
        :type surface: pygame.Surface
        """
        self.surface = surface

    def draw_item(self, menu_item, index, pos, margin_top):
        """draw a specific MenuItem

        :param menu_item: MenuItem to draw
        :type menu_item: MenuItem
        :param index: position of the MenuItem in the Menu used to highlight the first item
        :type index: int
        :param pos: position of the currently selected item in the Menu used to highlight the selected item
        :type pos: int
        :param margin_top: vertical position where this item will be rendered
        :type margin_top: int
        :return: the rendered MenuItem's rect
        :rtype: pygame.Rect
        """
        menu_item.rect.centerx = self.surface.get_rect().centerx
        menu_item.rect.centery = margin_top
        menu_item.hovered = True if index is 0 or index is pos else False
        menu_item.draw()

        return menu_item.get_rect()

    def print_menu(self, new_pos=1, old_pos=1, complete=True, start_pos=1):
        length = self.length
        rects = []

        if length - 1 <= new_pos:
            new_pos = length - 1

        margin_top = self.menu_items[0].get_size()
        margin_bottom = self.surface.get_height() - 2 * margin_top
        regular_size = self.menu_items[1].get_size() * 1.5
        space_needed = length * regular_size

        if complete:
            self.surface.fill(BACKGROUND)
            # always draw the first item (header)
            rects.append(self.draw_item(self.menu_items[0], 0, new_pos, margin_top))
            margin_top += self.menu_items[1].size

            for menu_index in range(start_pos, length):
                menu_item = self.menu_items[menu_index]
                margin_top += menu_item.get_size() * 1.5
                rects.append(self.draw_item(self.menu_items[menu_index], menu_index, new_pos, margin_top))
        else:
            new_option = self.menu_items[new_pos]
            old_option = self.menu_items[old_pos]

            if space_needed > margin_bottom:
                if new_pos < old_pos:
                    self.print_menu(new_pos, old_pos, True, new_pos)
                else:
                    self.print_menu(new_pos, old_pos, True, old_pos)

            new_option.hovered = True
            old_option.hovered = False

            new_option.draw()
            old_option.draw()

            rects.append(new_option.get_rect())
            rects.append(old_option.get_rect())

        return rects


class MenuItem(object):
    hovered = False

    def __init__(self, text, action, size=36):
        self.menu = None
        self.text = text
        self.action = action
        self.size = size
        self.font = pygame.font.Font(MENU_FONT, size)
        self.font_renderer = self.font.render(self.text, True, self.get_color())
        self.rect = self.font_renderer.get_rect()
        self.set_rect()

    def draw(self):
        self.set_renderer()
        self.menu.get_surface().blit(self.font_renderer, self.rect)

    def get_rect(self):
        return self.rect

    def set_renderer(self):
        self.font_renderer = self.font.render(self.text, True, self.get_color())

    def get_color(self):
        if self.hovered:
            return (255, 255, 255)
        else:
            return (100, 100, 100)

    def set_rect(self):
        self.set_renderer()
        self.rect = self.font_renderer.get_rect()

    def get_action(self):
        return self.action

    def get_size(self):
        return self.size

    def set_menu(self, menu):
        self.menu = menu

    def set_text(self, text):
        self.text = text
