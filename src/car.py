import pygame, os, math, random, const, config, sprite

DRIVE = 0
STOP = 1

class Car:
    

    
    cars = ['redcar-', 'whitecar-', 'yellowcar-']
    dirs = {const.LEFT:"left", const.UP:"up", const.RIGHT:"right", const.DOWN:"down"} 
    
    def __init__(self, maxVelocity, direction, optimalDistance, cfg, res):        
        self.sprite = sprite.Sprite(random.choice(self.cars) + self.dirs[direction], res, None, const.ORIGIN_TOP_LEFT)
        self.position = [0,0]        
        self.size = self.sprite.getSize()
        self.carAhead = None
        self.objectAhead = None
        self.velocity = 0
        self.safeDistance = 10
        self.optimalDistance = optimalDistance
        self.maxVelocity = maxVelocity
        self.direction = direction
        self.sensitivity = 0.4
        self.state = DRIVE
        self.acceleration = 0.0
        self.cfg = cfg
        self.distance = 0.0
        self.collides = False

    def setCarAhead(self, car):
        self.carAhead = car
        self.objectAhead = self.carAhead
        
    def setObjectAhead(self, object):
        self.objectAhead = object
        
    def followCar(self):
        self.objectAhead = self.carAhead

    def getDistance(self, object):        
        if self.direction == const.RIGHT:
            distance = object.getPosition()[0] - (self.position[0] + self.size[0])
        elif self.direction == const.LEFT:
            distance = self.position[0] - object.getPosition()[0] - object.getSize()[0]
        elif self.direction == const.DOWN:
            distance = object.getPosition()[1] - (self.position[1] + self.size[1])
        elif self.direction == const.UP:
            distance = self.position[1] - object.getPosition()[1] - object.getSize()[1]
        if distance < 0:    
            if self.direction == const.RIGHT or self.direction == const.LEFT:
                distance = self.cfg.board_size[0] + distance - self.size[0]
            else:
                distance = self.cfg.board_size[1] + distance - self.size[1]
        return distance

    def setPosition(self, x, y):
        if x < 0:
            x = self.cfg.board_size[0] + x - self.size[0]
        elif x + self.size[0] > self.cfg.board_size[0]:
            x = 0
        self.position[0] = x
        
        if y < 0:
            y = self.cfg.board_size[1] + y - self.size[1]
        elif y + self.size[1] > self.cfg.board_size[1]:
            y = 0
        self.position[1] = y

    def getPosition(self):
        return self.position

    def __V__(self, dx):
        return 0.5 * math.tanh(dx - self.safeDistance) + 0.5
    
    def update(self, dt, cars, enemies):
        self.sprite.update(dt)
        lastX = self.position[0]
        lastY = self.position[1]
        if self.objectAhead:                    
            a = self.__V__(self.getDistance(self.objectAhead)) * self.maxVelocity - self.velocity
            if a < 0:
                self.acceleration = a
            else:
                self.acceleration = self.sensitivity * a
        self.velocity = max(0, min(self.maxVelocity, self.velocity + self.acceleration))
        if self.velocity > 0.05:
            x = self.position[0] + self.velocity * self.direction[0] * dt
            y = self.position[1] + self.velocity * self.direction[1] * dt
            self.setPosition(x, y)
            aabb = self.aabb()
            for c in cars:
                if c.direction in const.opposite[self.direction] and self.aabb_collision(aabb, c.aabb()):
                    self.setPosition(lastX, lastY)
                    return      
            for e in enemies:
                if self.aabb_collision(aabb, e.aabb()):
                    self.setPosition(lastX, lastY)
                    return                        

    def aabb_collision(self, (minx1, miny1, maxx1, maxy1), (minx2, miny2, maxx2, maxy2)):
        xcollision = (minx1 <= minx2 and minx2 <= maxx1) or (minx2 <= minx1 and minx1 <= maxx2)
        ycollision = (miny1 <= miny2 and miny2 <= maxy1) or (miny2 <= miny1 and miny1 <= maxy2)
        return xcollision and ycollision
            
    def display(self, screen):
        self.sprite.display(screen, self.getPosition())            
            
    def start(self):
        self.objectAhead = self.carAhead
        self.state = DRIVE
        
    def stop(self, object):
        if self.state == STOP and self.getDistance(object) > self.getDistance(self.objectAhead):
            return
        self.objectAhead = object
        self.state = STOP       
        
    
    def aabb(self):
        return (self.position[0], self.position[1], self.position[0] + self.size[0], self.position[1] + self.size[1])
    
    def getSize(self):
        return self.size      
    
    def isInFront(self, object):
        ycollision = (self.position[1] <= object.getPosition()[1] and object.getPosition()[1] <= self.position[1] + self.getSize()[1]) or (object.getPosition()[1] <= self.position[1] and self.position[1] <= object.getPosition()[1] + object.getSize()[1])
        xcollision = (self.position[0] <= object.getPosition()[0] and object.getPosition()[0] <= self.position[0] + self.getSize()[0]) or (object.getPosition()[0] <= self.position[0] and self.position[0] <= object.getPosition()[0] + object.getSize()[0])
        
        if self.direction == const.LEFT and ycollision and object.getPosition()[0] < self.position[0]:
            return True 
        elif self.direction == const.RIGHT and ycollision and object.getPosition()[0] + object.getSize()[0] > self.position[0] + self.size[0]:
            return True
        elif self.direction == const.UP and xcollision and object.getPosition()[1] < self.position[1]:
            return True
        elif self.direction == const.DOWN and xcollision and object.getPosition()[1] + object.getSize()[1] > self.position[1] + self.size[1]:
            return True        
        
        return False
        
        
