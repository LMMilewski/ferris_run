import pygame
import math
import random

class CopSprite(pygame.sprite.Sprite):
    def __init__(self, x, y):
        self.r = 25;
        pygame.sprite.Sprite.__init__(self);
        self.x = x - self.r;
        self.y = y - self.r;
        self.alpha = 0;
        
    def update(self):
        self.image = pygame.surface.Surface((self.r*2, self.r*2));
        self.rect = self.image.get_rect();
        pygame.draw.circle(self.image, pygame.Color(0, 0, 128), self.rect.center, self.r);
        pygame.draw.line(self.image, pygame.Color(0, 0, 0), self.rect.center, (self.rect.center[0] + math.cos(self.alpha) * self.r, self.rect.center[1] + math.sin(self.alpha) * self.r));
        self.image.set_colorkey(pygame.Color('black'));
        self.rect.center = (self.x, self.y);
        
    def SetPosition(self, x, y, alpha):
        self.x = x - self.r;
        self.y = y - self.r;
        self.alpha += alpha;
        
        

class Cop():
    def InitMovement(self, start, end):
        self.direction = (self.end[0] - self.start[0], self.end[1] - self.start[1]);
        direction_length = pow(pow(self.direction[0], 2) + pow(self.direction[1], 2), 0.5);
        if (direction_length == 0):
            self.direction = (0, 0);
        else:
            self.direction = (self.direction[0]/direction_length, self.direction[1]/direction_length); 
        self.x = start[0];
        self.y = start[1];
        self.rotation_time = 0;
        self.sign = 1;
        
    def __init__(self, starting_x, starting_y, destination_x, destination_y):
        self.cop_sprite = CopSprite(starting_x, starting_y);
        self.start = (starting_x, starting_y);
        self.end = (destination_x, destination_y);
        self.InitMovement(self.start, self.end);
        self.speed = 10;
    
    def GetSprite(self):
        return self.cop_sprite;
    
    def update(self, dt):
        self.rotation_time += dt;
        if (self.rotation_time > 1000):
            self.sign = random.randint(0, 2) - 1;
            self.rotation_time = 0;
        self.cop_sprite.SetPosition(self.x, self.y, self.sign * 0.00405);