from player import *

GRAVITY = 1

worldGroup = pygame.sprite.Group()
playerGroup = pygame.sprite.Group()



def init():
    player = Player()
    playerGroup.add(player)
    
    
def update():
    """updates all physics components"""
    playerGroup.draw()
    playerGroup.update()

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
                pygame.sprite.Sprite.__init__(self, world)