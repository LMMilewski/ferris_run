import pygame

class CopSprite(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self);
        self.image = pygame.surface.Surface((50, 50));
        self.rect = self.image.get_rect();
        print "Circe " + str(self.rect.centerx) + ", " + str(self.rect.centery);
        pygame.draw.circle(self.image, pygame.Color(0, 0, 128), self.rect.center, 25);
        self.image.set_colorkey(pygame.Color('black'));
        self.rect.center = x-25, y-25;
        

class Cop():
    def __init__(self, x, y, starting_x, starting_y, destinatopn_x, destination_y):
        self.cop_sprite = CopSprite(x, y);