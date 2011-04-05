import pygame
from pygame.locals import *

import math

from config import *
from game_fsm import *
from resources import *
from sprite import *
from const import *
from random import *

def distance(pos1, pos2):
    dx = pos1[0] - pos2[0]
    dy = pos1[1] - pos2[1]
    return math.sqrt(dx*dx + dy*dy)

def direction_to_vector(direction):
    if direction == DIR_LEFT:
        return (-1,0)
    if direction == DIR_DOWN:
        return (0,1)
    if direction == DIR_RIGHT:
        return (1,0)
    if direction == DIR_UP:
        return (0,-1)
    if direction == DIR_STOP:
        return (0,0)

def direction_to_target(position, target):
    """
    assuming you can go in X or Y direction, try to shorten larger of
    distances: distances in x, distances in y
    """
    if target == None:
       return (-1,0)
    else:
        target_dx = target[0] - position[0]
        target_dy = target[1] - position[1]
        if abs(target_dx) > abs(target_dy):
            return DIR_LEFT if target_dx < 0 else DIR_RIGHT
        else:
            return DIR_UP if target_dy < 0 else DIR_DOWN

def get_next_position(cfg, position, direction, dt, speed):
    dx, dy = direction_to_vector(direction)
    px, py = position

    px, py = px + dx * dt * speed, py + dy * dt * speed

    # the board is a cylinder (its edges are glued together)
    if px < -5:
        px = cfg.board_size[0]+5
    if px > cfg.board_size[0]+5:
        px = -5
    if py < -5:
        py = cfg.board_size[1]+5
    if py > cfg.board_size[1]+5:
        py = -5
    return px, py

class Ferris:
    def __init__(self, cfg, res):
        self.cfg = cfg
        self.res = res

        self.sprite = [ Sprite("ferris-left", self.res, 0.5),
                        Sprite("ferris-down", self.res, 0.5),
                        Sprite("ferris-right", self.res, 0.5),
                        Sprite("ferris-up", self.res, 0.5) ]
        self.direction = DIR_LEFT
        self.speed = self.cfg.ferris_speed
        self.position = (300,300)

    def update(self, dt):
        self.sprite[self.direction].update(dt)
        self.position = get_next_position(self.cfg, self.position, self.direction, dt, self.speed)

    def display(self, screen):
        self.sprite[self.direction].display(screen, self.position)

# should refactor? the code is the same as Ferris's
class Director:
    def __init__(self, cfg, res, ferris):
        self.cfg = cfg
        self.res = res
        self.ferris = ferris

        self.sprite = [ Sprite("director-left", self.res, 0.25),
                        Sprite("director-down", self.res, 0.25),
                        Sprite("director-right", self.res, 0.25),
                        Sprite("director-up", self.res, 0.25) ]
        self.direction = DIR_LEFT
        self.speed = self.cfg.director_speed
        self.position = (500,500)
        self.target = None

    def update(self, dt):
        self.sprite[self.direction].update(dt)
        self.target = self.ferris.position
        self.direction = direction_to_target(self.position, self.target)
        self.position = get_next_position(self.cfg, self.position, self.direction, dt, self.speed)

    def display(self, screen):
        self.sprite[self.direction].display(screen, self.position)

class Sister:
    def __init__(self, cfg, res, ferris):
        self.cfg = cfg
        self.res = res
        self.ferris = ferris

        self.sprite = [ Sprite("sister-left", self.res, 0.25),
                        Sprite("sister-down", self.res, 0.25),
                        Sprite("sister-right", self.res, 0.25),
                        Sprite("sister-up", self.res, 0.25) ]
        self.direction = DIR_LEFT
        self.speed = self.cfg.sister_speed
        self.position = (100,100)
        self.target = None

    def update(self, dt):
        self.sprite[self.direction].update(dt)

        if distance(self.ferris.position, self.position) < 70:
            self.target = self.ferris.position
        else:
            ferris_dir = direction_to_vector(self.ferris.direction)
            self.target = self.ferris.position[0] + ferris_dir[0] * 80, self.ferris.position[1] + ferris_dir[1] * 80

        new_direction = direction_to_target(self.position, self.target)
        if new_direction != (self.direction + 2) % 4: # can't reverse direction
            self.direction = new_direction
        self.position = get_next_position(self.cfg, self.position, self.direction, dt, self.speed)

    def display(self, screen):
        self.sprite[self.direction].display(screen, self.position)


class Dictionary:
    def __init__(self, cfg, res, random):
        self.cfg = cfg
        self.res = res
        self.sprite = Sprite("dictionary", self.res, 0.25)
        self.position = (random.integer(20,580), random.integer(20,580))

    def update(self, dt):
        self.sprite.update(dt)

    def display(self, screen):
        self.sprite.display(screen, self.position)


class FerrisRunGame(GameState):
    def __init__(self, cfg, res):
        self.cfg = cfg
        self.res = res

        self.random = Random()

        self.__is_finished = False
        self.level_num = None # set in set_level called from init
        self.ferris = Ferris(cfg, res)
        self.director = Director(cfg, res, self.ferris)
        self.sister = Sister(cfg, res, self.ferris)
        self.dictionary = Dictionary(cfg, res, self.random)

        self.background = Sprite("background", self.res, None, ORIGIN_TOP_LEFT)
        self.hud = Sprite("hud", self.res, None, ORIGIN_TOP_LEFT)

    def init(self, screen):
        self.set_level(1)

    def set_level(self, level_num):
        self.level_num = level_num
        self.res.music_play("level_background")
        self.res.sounds_play("level_start")

    def go_to_next_level(self):
        self.set_level(self.level_num + 1)

    def update(self, dt):
        self.background.update(dt)
        self.hud.update(dt)

        if self.cfg.print_fps:
            print dt, " ", int(1.0/dt)

        self.ferris.update(dt)
        self.director.update(dt)
        self.sister.update(dt)
        self.dictionary.update(dt)

    def process_event(self, event):
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                self.finish()
            if event.key == K_LEFT:
                self.ferris.direction = DIR_LEFT
            if event.key == K_RIGHT:
                self.ferris.direction = DIR_RIGHT
            if event.key == K_UP:
                self.ferris.direction = DIR_UP
            if event.key == K_DOWN:
                self.ferris.direction = DIR_DOWN
            if event.key == K_1:
                self.cfg.print_fps = not self.cfg.print_fps

    def display(self, screen):
        self.background.display(screen, (0,0))
        self.dictionary.display(screen)
        self.ferris.display(screen)
        self.director.display(screen)
        self.sister.display(screen)
        board_size = self.cfg.board_size[0]
        self.hud.display(screen, (board_size,0))

    def finish(self):
        self.__is_finished = True

    def is_finished(self):
        return self.__is_finished

def main():
    cfg = Config()
    fsm = GameFsm(cfg)
    res = Resources(cfg).load_all()
    fsm.set_state(FerrisRunGame(cfg,res))
    pygame.display.set_caption("Ferris Run")
    pygame.mouse.set_visible(not cfg.fullscreen)
    fsm.run()
