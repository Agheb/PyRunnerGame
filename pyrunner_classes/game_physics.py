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
        col = pygame.sprite.groupcollide(playerGroup, worldGroup, False, False)
        for playerObj in col.keys() :
            if len(col) > 0 :
                for sprite in col[playerObj] :
                    self.fixPos(playerObj,sprite)
            else:
                playerObj.onGround = False
    def fixPos(self,player, sprite):
        player.onGround = True
class Collider():
    def __init__(self, player):
        self.player = player
        self.objects = [player]
        
    def add_object(self, object):
        self.objects.append(object)
        
    def collide(self, tet):
        pass

class WorldObject(pygame.sprite.Sprite):
    def __init__(self, tile):
        (pos_x, pos_y,self.image) = tile
        pygame.sprite.Sprite.__init__(self, worldGroup)
        self.rect = self.image.get_rect()
        self.rect.x = pos_x * TILE_WIDTH
        self.rect.y = pos_y * TILE_HEIGHT
    def update(self):
        pass
        