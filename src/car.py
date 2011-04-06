import pygame, os, math, random, const, config

DRIVE = 0
STOP = 1

class Car(pygame.sprite.Sprite):
    

    
    cars = ['redcar.png', 'whitecar.png', 'yellowcar.png']
    
    def __init__(self, maxVelocity, direction, cfg):
        pygame.sprite.Sprite.__init__(self) #call Sprite intializer
        self.image = pygame.image.load(os.path.join('gfx', random.choice(self.cars)))
        if direction == const.LEFT:
            self.image = pygame.transform.rotate(self.image, 180)
        elif direction == const.UP:
            self.image = pygame.transform.rotate(self.image, 90)
        elif direction == const.DOWN:
            self.image = pygame.transform.rotate(self.image, 270)
        self.rect = self.image.get_rect()
        self.carAhead = None
        self.objectAhead = None
        self.velocity = 0
        self.safeDistance = 10
        self.maxVelocity = maxVelocity
        self.direction = direction
        self.sensitivity = 0.5
        self.state = DRIVE
        self.acceleration = 0.0
        self.cfg = cfg
        self.distance = 0.0

    def setCarAhead(self, car):
        self.carAhead = car
        self.objectAhead = self.carAhead
        
    def setObjectAhead(self, object):
        self.objectAhead = object
        
    def followCar(self):
        self.objectAhead = self.carAhead

    def __getDistance__(self, object):        
        if self.direction == const.RIGHT:
            distance = object.getPosition()[0] - (self.rect[0] + self.rect[2])
        elif self.direction == const.LEFT:
            distance = self.rect[0] - object.getPosition()[0] - object.getSize()[0]
        elif self.direction == const.DOWN:
            distance = object.getPosition()[1] - (self.rect[1] + self.rect[3])
        elif self.direction == const.UP:
            distance = self.rect[1] - object.getPosition()[1] - object.getSize()[1]
        if distance < 0:    
            if self.direction == const.RIGHT or self.direction == const.LEFT:
                distance = self.cfg.board_size[0] + distance - self.rect[2]
            else:
                distance = self.cfg.board_size[1] + distance - self.rect[3]
        return distance

    def setPosition(self, x, y):
        if x < 0:
            x = self.cfg.board_size[0] + x - self.rect[2]
        elif x + self.rect[2] > self.cfg.board_size[0]:
            x = 0
        self.rect[0] = x
        
        if y < 0:
            y = self.cfg.board_size[1] + y - self.rect[3]
        elif y + self.rect[3] > self.cfg.board_size[1]:
            y = 0
        self.rect[1] = y

    def getPosition(self):
        return (self.rect[0], self.rect[1])

    def __V__(self, dx):
        return 0.5 * math.tanh(dx - self.safeDistance) + 0.5
    
    def update(self):
        if self.objectAhead:        
            self.acceleration = self.sensitivity * (self.__V__(self.__getDistance__(self.objectAhead)) * self.maxVelocity - self.velocity)
            
        self.velocity = max(0, min(self.maxVelocity, self.velocity + self.acceleration))
        self.distance += self.velocity
        self.rect.move_ip(self.distance * self.direction[0], self.distance * self.direction[1])   
        self.distance = self.distance - math.floor(self.distance)     
        self.setPosition(self.rect[0], self.rect[1])
            
    def start(self):
        self.objectAhead = self.carAhead
        
    def stop(self, object):
        self.objectAhead = object       
        
    
    def aabb(self):
        return (self.rect[0] + 2, self.rect[1] + 2, self.rect[0] + self.rect[2] - 4, self.rect[1] + self.rect[3] - 4)
    
    def getSize(self):
        return (self.rect[2], self.rect[3])    
        
        
        
        
        