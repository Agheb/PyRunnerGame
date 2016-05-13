import pygame
from pygame.locals import *
import settings

BLACK = pygame.Color(0, 0, 0)

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


def print_pygame_text(screen, textstring, center_x=False, offset_x=0, offset_y=20, size=36, text_color=BLACK, bkgr=SRCALPHA):

    pygame.font.init()
    """print some text in the pygame window"""
    textfont = "./resources/fonts/Angeline_Vintage_Demo.otf"
    font = pygame.font.Font(textfont, size)
    text = font.render(textstring, 1, text_color, bkgr)
    textpos = text.get_rect()
    # center text on x axis
    if center_x:
        textpos.centerx = screen.get_rect().centerx
    else:
        textpos.centerx = offset_x
    # move text on y axis
    textpos.centery = offset_y
    # draw text to screen
    screen.blit(text, textpos)


# menu functions
def menu_back():
    pass


def menu_new_game():
    pass

def menu_new_game_singleplayer():
    pass


def menu_new_game_start_game():
    """for single and multiplayer games"""
    pass


def menu_singleplayer():
    pass


def menu_multiplayer():
    pass


def menu_multiplayer_lan():
    pass


def menu_options():
    pass


def menu_options_video():
    pass


def menu_options_controls():
    pass


m_back = "Back"
