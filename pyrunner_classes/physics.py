GRAVITY = 1

worldGroup = pygame.sprite.Group()
playerGroup = pygame.sprite.Group()



class Collider():
    def __init__(self, player):
        self.player = player
        self.objects = [player]
        
    def add_object(self, object):
        self.objects.append(object)
        
    def collide(self, tet):
        pass


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, playerGroup)
        self.speed_x = 0
        self.speed_y = GRAVITY
        self.image = TODO
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.y += self.speed_x
        self.rect.x += self.speed_y
        self.rect.x 

    def collide(self):
        collisions = pygame.sprite.spritecollide(self,worldGroup,False)
        for item in collisions:
            if item != self:
                print(item)
                self.stop()
                
                
    def stop(self):
        self.speed_x = 0
        self.speed_y = 0
        return 
    

class WorldObject(pygame.sprite.Sprite):
    def __init__(self):
                pygame.sprite.Sprite.__init__(self, world)