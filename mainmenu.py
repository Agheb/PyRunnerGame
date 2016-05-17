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
screen = None


class Menu(object):

    def __init__(self, scr):
        global screen
        screen = scr
        pygame.font.init()
        # display = pygame.display.Info()
        # width, height = display.current_w, display.current_h
        # print(str(width) + "/" + str(height))
        # screen = pygame.Surface((width, height))


class MenuItem(object):
    hovered = False

    def __init__(self, text, action, pos_y, size=36, parent_menu=None):
        self.text = text
        self.action = action
        self.pos_y = pos_y
        self.size = size
        self.parent_menu = parent_menu
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
        # and position at y
        self.rect.centery = self.pos_y

    def get_action(self):
        return self.action

    def set_pos_y(self, pos):
        self.pos_y = pos


def print_menu(options, new_pos=1, old_pos=1, complete=True):
    # while True:
        # pygame.event.pump()
    screen_resolution = pygame.display.Info()
    s_width, s_height = screen_resolution.current_w, screen_resolution.current_h
    textsize = 0
    for i in range(0, len(options)):
        textsize += options[i].size
    margin_y = (s_height - textsize) / (len(options) + 2)
    rects = []

    if complete:
        for x in range(0, len(options)):
            option = options[x]
            option.set_pos_y(margin_y * x + margin_y)
            pygame.draw.rect(screen, BACKGROUND, option.get_rect())

            if x is 0:
                option.hovered = True
            else:
                if x is new_pos:  # option.rect.collidepoint(pygame.mouse.get_pos()):
                    option.hovered = True
                else:
                    option.hovered = False

            option.draw()
            rects.append(option.get_rect())
    else:
        new_option = options[new_pos]
        old_option = options[old_pos]

        new_option.hovered = True
        old_option.hovered = False

        new_option.draw()
        old_option.draw()

        rects.append(new_option.get_rect())
        rects.append(old_option.get_rect())

    return rects
