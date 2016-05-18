import pygame
from pygame.locals import *
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
screen = pygame.display.set_mode((800, 600), RESIZABLE, 32)


class Menu(object):

    def __init__(self, parent=None):
        self.surface = None
        self.parent = parent
        self.menu_items = []
        if self.parent:
            self.add_menu_item(MenuItem("Back", self.parent))
        pygame.font.init()

    def add_menu_item(self, menu_item):
        if self.parent:
            # keep the back button at the end of the menu items list
            self.menu_items.insert(len(self.menu_items) - 1, menu_item)
        else:
            self.menu_items.append(menu_item)

    def get_surface(self):
        return self.surface

    def set_surface(self, surface):
        self.surface = surface

    def print_menu(self, new_pos=1, old_pos=1, complete=True):
        screen_resolution = pygame.display.Info()
        s_width, s_height = screen_resolution.current_w, screen_resolution.current_h
        length = len(self.menu_items)

        rects = []

        if complete:
            for menu_index in range(0, length):
                option = self.menu_items[menu_index]
                option.get_rect().centery = (menu_index + 1) * option.get_size() * 1.5

                # pygame.draw.rect(screen, BACKGROUND, option.get_rect())
                if menu_index is 0:
                    option.hovered = True
                else:
                    if menu_index is new_pos:  # option.rect.collidepoint(pygame.mouse.get_pos()):
                        option.hovered = True
                    else:
                        option.hovered = False

                option.draw()
                rects.append(option.get_rect())
        else:
            new_option = self.menu_items[new_pos]
            old_option = self.menu_items[old_pos]

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
        self.text = text
        self.action = action
        self.size = size
        self.font = pygame.font.Font(MENU_FONT, size)
        self.font_renderer = self.font.render(self.text, True, self.get_color())
        self.rect = self.font_renderer.get_rect()
        self.set_rect()
        self.draw()

    def draw(self):
        self.set_renderer()
        screen.blit(self.font_renderer, self.rect)

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
        # center vertically
        self.rect.centerx = screen.get_rect().centerx

    def get_action(self):
        return self.action

    def switch_menu(self):
        if self.action is Menu:
            self.action.print_menu(0, 0, True)

    def get_size(self):
        return self.size


if __name__ == "__main__":
    pygame.init()
    menu = Menu()
    menu.add_menu_item(MenuItem("Hallo", None))
    menu.add_menu_item(MenuItem("Welt ist extrem viel breiter", None))
    menu.add_menu_item(MenuItem("Exit", None))
    menu2 = Menu(menu)
    menu2.add_menu_item(MenuItem("Hallo", None))
    menu2.add_menu_item(MenuItem("Menu 2", None))

    while True:
        screen.fill(BACKGROUND)
        pygame.time.Clock().tick(1)
        pygame.display.update(menu2.print_menu(0, 0, True))
