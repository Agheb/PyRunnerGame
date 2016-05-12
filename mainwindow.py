import pygame
from pygame.locals import *
from sys import exit
import settings
screen = fps = game_is_running = None


def quit_game():
    """quit the game"""
    pygame.quit()
    exit()


def init_game():
    """initialize the game variables"""
    global screen, fps, game_is_running
    # initialize main screen
    settings.set_is_running(True)
    settings.init_screen()
    screen = settings.get_screen()
    fps = settings.get_fps()
    game_is_running = settings.get_is_running()


def start_game():
    """start the game"""
    global screen_x, screen_y, screen, fps
    # PyGame initialization
    pygame.init()
    init_game()
    clock = pygame.time.Clock()
    refresh_counter = 0

    # init screen
    settings.refresh_screen()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                quit_game()
            elif event.type == VIDEORESIZE:
                x, y = event.dict['size']
                settings.set_resolution(x, y)
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    quit_game()
                if game_is_running:
                    if K_0 <= event.key <= K_9:
                        pass
                    if event.key == K_LEFT:
                        pass
                    if event.key == K_RIGHT:
                        pass
                    if event.key == K_SPACE or event.key == K_DOWN:
                        pass
                    # lazy update the screen, only if a key was pressed while the game is running
                    settings.refresh_screen()
                else:
                    if event.key == K_n:
                        player_one_starts = True
                        init_game()
                    if event.key == K_r:
                        init_game()
            # in case the game board disappears after switching to full screen on macos x
            elif event.type == MOUSEBUTTONDOWN:
                if game_is_running:
                    settings.refresh_screen()
                # x, y = pygame.mouse.get_pos()

        # save cpu resources
        clock.tick(fps)

        """
        update screen at least once every second

        seems like % is really slow
        replacing this with refresh_counter % fps is 0
        consumes 50% of one core from a 2,4 GHz Core i7
        just comparing values consumes ten times less (~5%)
        """
        if fps <= refresh_counter:
            settings.refresh_screen()
            refresh_counter = 0
        else:
            refresh_counter += 1


# start the 4 in a row game
start_game()
