import pygame
import math

class CopSprite(pygame.sprite.Sprite):
    def __init__(self, x, y, alpha):
        self.r = 25;
        if (alpha > 180):
            self.alpha = -alpha + 180;
        else:
            self.alpha = alpha;
        pygame.sprite.Sprite.__init__(self);
        self.x = x;
        self.y = y;
        self.frame_counter = 0;
        self.image_original =[pygame.transform.scale(pygame.image.load("../gfx/cop_0.png"), (100, 100)), pygame.transform.scale(pygame.image.load("../gfx/cop_1.png"), (100, 100))];
        
    def update(self):
        self.frame_counter +=1;
        self.image = pygame.transform.rotate(self.image_original[(self.frame_counter / 100) % len(self.image_original)], self.alpha);
        self.rect = self.image.get_rect(center=(self.x, self.y));
        
    def SetPosition(self, x, y, alpha):
        self.x = x - self.r;
        self.y = y - self.r;
        self.alpha = -alpha;

class Cop():
    def InitMovement(self, start, end):
        self.direction = (end[0] - start[0], end[1] - start[1]);
        direction_length = pow(pow(self.direction[0], 2) + pow(self.direction[1], 2), 0.5);
        if (direction_length == 0):
            self.direction = (0, 0);
        else:
            self.direction = (self.direction[0]/direction_length, self.direction[1]/direction_length); 
        self.x = start[0];
        self.y = start[1];
        self.speed = 30;
        self.rotation_speed = 30;
        self.path_length = direction_length;
        self.destination_angle = math.degrees(math.acos(self.direction[0]));

        if (math.copysign(1, self.direction[1]) != math.copysign(1, math.sin(self.destination_angle))):
            self.destination_angle = 360 - self.destination_angle;
                
        self.start = start;
        self.end = end;
        
    def __init__(self, starting_x, starting_y, destination_x, destination_y):
        self.start = (starting_x, starting_y);
        self.end = (destination_x, destination_y);
        self.destination_angle = 0;
        self.angle = 0;
        self.InitMovement(self.start, self.end);
        self.cop_sprite = CopSprite(starting_x, starting_y, self.angle);
        self.angle = self.destination_angle;
    
    def GetSprite(self):
        return self.cop_sprite;
    
    def update(self, dt):
        if (self.destination_angle != self.angle):
            if (math.fabs(self.destination_angle - self.angle) < dt * self.rotation_speed):
                self.angle = self.destination_angle;
            else:
                dangle = math.copysign(dt * self.rotation_speed, self.destination_angle - self.angle);
                self.angle += dangle;
            if (self.angle < 0):
                self.angle += 360;
            if (self.angle > 360):
                self.angle -=360;
        else:
            dx = self.direction[0] * dt * self.speed;
            dy = self.direction[1] * dt * self.speed;
            self.x = self.x + dx;
            self.y = self.y + dy;

            if (pow(pow(self.x - self.start[0], 2) + pow(self.y - self.start[1], 2), 0.5) >= self.path_length):
                new_start = self.end;
                new_end = self.start;
                self.InitMovement(new_start, new_end);
        
        self.cop_sprite.SetPosition(int(self.x), int(self.y), self.angle);