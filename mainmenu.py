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
        self.items_count = 0
        if self.parent:
            self.add_menu_item(MenuItem("Back", self.parent))
        pygame.font.init()

    def add_menu_item(self, menu_item):
        # keep the back button at the end of the menu items list
        self.menu_items.insert(self.items_count - 1, menu_item)
        print(str(self.items_count))
        self.items_count += 1

        print(str(self.items_count))

    def get_surface(self):
        return self.surface

    def set_surface(self, surface):
        self.surface = surface

    def print_menu(self, new_pos=1, old_pos=1, complete=True):
        screen_resolution = pygame.display.Info()
        s_width, s_height = screen_resolution.current_w, screen_resolution.current_h
        textsize = 0
        length = int(self.items_count)
        for i in range(0, length):
            textsize += self.menu_items[i].size
        margin_y = (s_height - textsize) / (length + 2)
        rects = []

        if complete:
            for menu_index in range(0, length):
                option = self.menu_items[menu_index]
                option.set_pos_y(margin_y * menu_index + margin_y)
                pygame.draw.rect(screen, BACKGROUND, option.get_rect())

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


if __name__ == "__main__":
    menu = Menu()
    Menu.add_menu_item(menu, MenuItem("Hallo", None))
    Menu.add_menu_item(menu, MenuItem("Welt", menu))

    while True:
        Menu.print_menu(0, 0, True)
        pygame.time.Clock().tick(5)

