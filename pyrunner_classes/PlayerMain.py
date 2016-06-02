import pygame
import constants
from player import Player


def main():
    """Main Program"""
    pygame.init()

    # set size
    size = (constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
    screen = pygame.display.set_mode(size)

    pygame.display.set_caption("PyRunner Player")

    # Create the player
    player = Player()

    active_sprite_list = pygame.sprite.Group()
    active_sprite_list.add(player)

    # for the game loop
    done = False

    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    # -------- Main Program Loop -----------
    while not done:
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                done = True  # Flag that we are done so we exit this loop

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.go_left()
                if event.key == pygame.K_RIGHT:
                    player.go_right()
                if event.key == pygame.K_UP:
                    player.go_up()
                if event.key == pygame.K_DOWN:
                    player.go_down()
                if event.key == pygame.K_a:
                    if player.change_y == 0 and player.change_x == 0:
                        player.dig_left()
                        print("a key")
                if event.key == pygame.K_s:
                    if player.change_y == 0 and player.change_x == 0:
                        player.dig_right()
                        print("s key")

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.change_x < 0:
                    player.stop()
                if event.key == pygame.K_RIGHT and player.change_x > 0:
                    player.stop()
                if event.key == pygame.K_DOWN and player.change_y < 0:
                    player.stop()
                if event.key == pygame.K_UP and player.change_y > 0:
                    player.stop()
                if event.key == pygame.K_a:
                    player.stop()
                if event.key == pygame.K_s:
                    player.stop()

        # Update the player
        active_sprite_list.update()

        # ALL CODE TO DRAW SHOULD GO BELOW THIS COMMENT

        pygame.Surface.fill(screen, (0, 0, 0))
        active_sprite_list.draw(screen)

        # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT

        # Limit to 60 frames per second
        clock.tick(60)

        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
