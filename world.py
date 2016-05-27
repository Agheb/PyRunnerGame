import pygame as pg
import tilerenderer
import os

"""Initialize pygame, create a clock, create the window
with a surface to blit the map onto."""
pg.init()
fps_clock = pg.time.Clock()
main_surface = pg.display.set_mode((420, 420))
main_rect = main_surface.get_rect()

"""loads the file """

## TODO: Set relative Path
dir = os.path.dirname(__file__)
tmx_file = os.path.join(dir, 'test.tmx')
tile_renderer = tilerenderer.Renderer(tmx_file)

"""Create the map surface using the make_level()
method.  Used to blit onto the main_surface."""
level_surface = tile_renderer.make_level()
map_rect = level_surface.get_rect()

"""Simple game loop that blits the map_surface onto
the main_surface."""


def main():
    while True:
        main_surface.blit(level_surface, map_rect)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

        pg.display.update()
        fps_clock.tick(30)


if __name__ == "__main__":
    main()
