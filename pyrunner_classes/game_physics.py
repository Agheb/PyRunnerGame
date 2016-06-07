from .player import *
import pygame
from pprint import pprint

GRAVITY = 1
MULTIPLICATOR = 1
TILE_WIDTH = 32
TILE_HEIGHT = 32


worldGroup = pygame.sprite.Group()
playerGroup = pygame.sprite.Group()

class Physics():
    def __init__(self, render_thread):
        self.gravity = GRAVITY
        self.render_thread = render_thread
        self.player = Player()
        playerGroup.add(self.player)
        return

    def update(self):
        """updates all physics components"""
        #TODO: pass sprites to render thread
        playerGroup.draw(self.render_thread.screen)
        worldGroup.draw(self.render_thread.screen)
        self.render_thread.refresh_screen(True)
        playerGroup.update()
        self.collide()
        return
    def collide(self):
      """calculates collision for players and sprites"""
      #TODO: add head collide
      col = pygame.sprite.groupcollide(playerGroup, worldGroup, False, False)
      if len(col) > 0:
        #some collision
        for playerObj in col.keys():
          for sprite in col[playerObj]:
            if sprite.climbable:
              playerObj.on_ladder = True
            else:
              #collision at feet
              self.fixPos(playerObj,sprite)
            """
            else:
              print("right %s" %sprite.rect.collidepoint(playerObj.rect.bottomright))
              print("left %s" %sprite.rect.collidepoint(playerObj.rect.bottomleft))
              print(sprite.rect.collidepoint(playerObj.rect.topright))
              print(sprite.rect.collidepoint(playerObj.rect.topleft))"""
      else:
        for player in playerGroup:
          player.on_ground = False
          player.on_ladder = False
    def fixPos(self,player, sprite):
        """Used tp place the player nicely"""
        player.on_ground = True
        player.rect.y = sprite.rect.y - player.rect.height -1

class WorldObject(pygame.sprite.Sprite):
    def __init__(self, tile, climbable = False):
        (pos_x, pos_y,self.image) = tile
        pygame.sprite.Sprite.__init__(self, worldGroup)
        self.rect = self.image.get_rect()
        self.rect.x = pos_x * TILE_WIDTH
        self.rect.y = pos_y * TILE_HEIGHT
        self.climbable = climbable
    def update(self):
        pass
