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

    def __init__(self, surface, parent=None):
        self.surface = surface
        self.parent = parent
        self.menu_items = []
        if self.parent:
            self.add_menu_item(MenuItem("Back", self.parent))
        pygame.font.init()

    def add_menu_item(self, menu_item):
        if self.parent:
            # keep the back button at the end of the menu items list
            self.menu_items.insert(self.get_length() - 1, menu_item)
        else:
            self.menu_items.append(menu_item)
        # finish initialization
        menu_item.set_menu(self)

    def get_menu_item(self, index):
        return self.menu_items[index]

    def get_length(self):
        return len(self.menu_items)

    def get_surface(self):
        return self.surface

    def set_surface(self, surface):
        self.surface = surface

    def print_item(self, menu_item, index, pos, margin_top):
        menu_item.rect.centerx = self.surface.get_rect().centerx
        menu_item.rect.centery = margin_top
        menu_item.hovered = True if index is 0 or index is pos else False
        menu_item.draw()

        return menu_item.get_rect()

    def print_menu(self, new_pos=1, old_pos=1, complete=True, start_pos=1):
        length = self.get_length()
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
            rects.append(self.print_item(self.menu_items[0], 0, new_pos, margin_top))
            margin_top += self.menu_items[1].size

            for menu_index in range(start_pos, length):
                menu_item = self.menu_items[menu_index]
                margin_top += menu_item.get_size() * 1.5
                rects.append(self.print_item(self.menu_items[menu_index], menu_index, new_pos, margin_top))
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
