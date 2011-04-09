import pygame, os, time

RED = 0
YELLOW_BEFORE_GREEN = 1
GREEN = 2
YELLOW_BEFORE_RED = 3


class TrafficLight(pygame.sprite.Sprite):



    SWITCHTIME = 10.0

    def __init__(self, initState, stopX, stopY):
        pygame.sprite.Sprite.__init__(self) #call Sprite intializer
        self.state = initState
        self.img = {}
        self.img[GREEN] = pygame.image.load(os.path.join('gfx', 'greenlight.png'))
        self.img[YELLOW_BEFORE_GREEN] = pygame.image.load(os.path.join('gfx', 'yellowlight.png'))
        self.img[YELLOW_BEFORE_RED] = pygame.image.load(os.path.join('gfx', 'yellowlight.png'))
        self.img[RED] = pygame.image.load(os.path.join('gfx', 'redlight.png'))
        self.image = self.img[self.state]
        self.rect = self.image.get_rect()
        self.stopPoint = (stopX, stopY)

        self.time = time.time()
        self.leftBound = 0
        self.rightBound = 0
        self.upperBound = 0
        self.bottomBound = 0
        self.resetState = initState

    def changeState(self):
        self.state = (self.state + 1) % 4
        self.image = self.img[self.state]

    def getState(self):
        return self.state

    def setPosition(self, x, y):
        self.rect[0] = x
        self.rect[1] = y

    def getPosition(self):
        return self.stopPoint

    def getSize(self):
        return (0,0)

    def reset(self):
        self.state = self.resetState

    def stop(self):
        self.state = YELLOW_BEFORE_RED

