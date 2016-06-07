from .player import *
import pygame

GRAVITY = 1
MULTIPLICATOR = 1


worldGroup = pygame.sprite.Group()

    
class Physics():
    def __init__(self, render_thread):
        self.gravity = GRAVITY
        self.render_thread = render_thread
        self.playerGroup = pygame.sprite.Group()
        self.player = Player()
        self.playerGroup.add(self.player)
        return

    def update(self):
        """updates all physics components"""
        #TODO: pass sprites to render thread
        self.playerGroup.draw(self.render_thread.screen)
        worldGroup.draw(self.render_thread.screen)
        self.render_thread.refresh_screen(True)
        self.playerGroup.update()
        self.collide()
        return
    def collide(self):
        for col in pygame.sprite.spritecollide(self.player, worldGroup, True):
            if col != self:
                print("collide")
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
        self.rect.x = pos_x
        self.rect.y = pos_y
        