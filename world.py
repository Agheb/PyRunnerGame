
import sys

import pygame as pg

from pyrunner_classes import *

"""Initialize pygame, create a clock, create the window
with a surface to blit the map onto."""
pg.init()
fps_clock = pg.time.Clock()
main_surface = pg.display.set_mode((1024, 768))
main_rect = main_surface.get_rect()

"""
loads the file
"""

tmx_file = "./resources/levels/scifi.tmx"
tile_renderer = Level(tmx_file,main_surface)

"""Create the map surface using the make_level()
method.  Used to blit onto the main_surface."""
level_surface = tile_renderer.make_level()
level_rect = level_surface.get_rect()

"""Simple game loop that blits the map_surface onto
the main_surface."""


def main():
    while True:
        main_surface.blit(level_surface, level_rect)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

        pg.display.update()
        fps_clock.tick(30)


if __name__ == "__main__":
    main()
