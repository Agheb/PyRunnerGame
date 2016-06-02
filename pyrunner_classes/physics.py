from .player import *

GRAVITY = 1

    
class Physics():
    def __init__(self):
        self.gravity = GRAVITY
        self.worldGroup = pygame.sprite.Group()
        self.playerGroup = pygame.sprite.Group()
        self.player = Player()
        self.playerGroup.add(player)
    def update(self):
        """updates all physics components"""
        self.playerGroup.draw()
        self.playerGroup.update()
    

class Collider():
    def __init__(self, player):
        self.player = player
        self.objects = [player]
        
    def add_object(self, object):
        self.objects.append(object)
        
    def collide(self, tet):
        pass

class WorldObject(pygame.sprite.Sprite):
    def __init__(self):
                pygame.sprite.Sprite.__init__(self, worldGroup)