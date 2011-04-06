import pygame
from pygame.locals import *

import math

from config import *
from game_fsm import *
from resources import *
from sprite import *
from const import *
from random import *

def aabb_collision((minx1, miny1, maxx1, maxy1), (minx2, miny2, maxx2, maxy2)):
    xcollision = (minx1 <= minx2 and minx2 <= maxx1) or ((minx2 <= minx1 and minx1 <= maxx2))
    ycollision = (miny1 <= miny2 and miny2 <= maxy1) or ((miny2 <= miny1 and miny1 <= maxy2))
    return xcollision and ycollision

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

    def aabb(self):
        return self.sprite[self.direction].aabb(self.position)

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

    def aabb(self):
        return self.sprite[self.direction].aabb(self.position)

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

    def aabb(self):
        return self.sprite[self.direction].aabb(self.position)

class Register:
    def __init__(self, cfg, res, random):
        self.cfg = cfg
        self.res = res
        self.sprite = Sprite("register", self.res, 0.25)
        self.position = (random.integer(20,580), random.integer(20,580))

    def update(self, dt):
        self.sprite.update(dt)

    def display(self, screen):
        self.sprite.display(screen, self.position)

    def aabb(self):
        return self.sprite.aabb(self.position)

class Car:
    def __init__(self, cfg, res, position, direction, color):
        self.cfg = cfg
        self.res = res

        self.position = position
        self.direction = direction
        self.color = color

        self.sprite = [ Sprite("car-left-"+color, self.res),
                        Sprite("car-down-"+color, self.res),
                        Sprite("car-right-"+color, self.res),
                        Sprite("car-up-"+color, self.res) ]

        self.speed = self.cfg.car_speed

    def update(self, dt):
        self.sprite[self.direction].update(dt)
        self.position = get_next_position(self.cfg, self.position, self.direction, dt, self.speed)

    def display(self, screen):
        self.sprite[self.direction].display(screen, self.position)

    def aabb(self):
        return self.sprite[self.direction].aabb(self.position)


class FerrisRunGame(GameState):
    def __init__(self, cfg, res):
        self.cfg = cfg
        self.res = res

        self.random = Random()

        self.__is_finished = False
        self.level_num = None # set in set_level called from init
        self.register = Register(cfg, res, self.random)

        self.background = Sprite("background", self.res, None, ORIGIN_TOP_LEFT)
        self.hud = Sprite("hud", self.res, None, ORIGIN_TOP_LEFT)

        self.cars = []
        car_colors = ["white", "red", "green", "blue"]
        for i in range(3):
            self.cars.append(Car(self.cfg, self.res, (390 + (i%3) * 20, i * 200), DIR_UP, car_colors[i % len(car_colors)]))
            self.cars.append(Car(self.cfg, self.res, (170 + (i%3) * 20, (i * 200 + 100) % 600), DIR_DOWN, car_colors[i % len(car_colors)]))
            self.cars.append(Car(self.cfg, self.res, (i * 200, 390 + (i%3) * 20), DIR_RIGHT, car_colors[i % len(car_colors)]))
            self.cars.append(Car(self.cfg, self.res, ((i * 200 + 100)%600, 170 + (i%3) * 20), DIR_LEFT, car_colors[i % len(car_colors)]))

        self.points = 0
        self.deaths = 0

        self.stopped = True # the game is not playing right now (characters don't move etc)

    def init(self, screen):
        self.set_level(1)

    def set_level(self, level_num):
        self.level_num = level_num
        self.reset_level()
        self.res.music_play("level_background")
        self.res.sounds_play("level_start")

    def reset_level(self):
        self.ferris = Ferris(self.cfg, self.res)
        self.director = Director(self.cfg, self.res, self.ferris)
        self.sister = Sister(self.cfg, self.res, self.ferris)
        self.stopped = True

    def go_to_next_level(self):
        self.set_level(self.level_num + 1)

    def update(self, dt):
        self.background.update(dt)
        self.hud.update(dt)

        if self.cfg.print_fps:
            print dt, " ", int(1.0/dt)

        if self.stopped:
            return

        # update all objects
        self.ferris.update(dt)
        self.director.update(dt)
        self.sister.update(dt)
        self.register.update(dt)
        for car in self.cars:
            car.update(dt)

        # check collision with register
        if aabb_collision(self.ferris.aabb(), self.register.aabb()):
            self.res.sounds_play("collect")
            self.register = Register(self.cfg, self.res, self.random)
            self.points += 100

        # check collision with enemies
        enemies = [self.director, self.sister] + self.cars
        for enemy in enemies:
            if aabb_collision(self.ferris.aabb(), enemy.aabb()):
                self.res.sounds_play("die")
                self.deaths += 1
                self.reset_level()
                return

    def process_event(self, event):
        if event.type == KEYDOWN:
            self.stopped = False
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
            if event.key == K_p:
                self.stopped = True
            if event.key == K_1:
                self.cfg.print_fps = not self.cfg.print_fps

    def display(self, screen):
        self.background.display(screen, (0,0))

        for car in self.cars:
            car.display(screen)

        self.register.display(screen)
        self.ferris.display(screen)
        self.director.display(screen)
        self.sister.display(screen)

        board_size = self.cfg.board_size[0]
        self.hud.display(screen, (board_size,0))

        level_label = self.res.font_render("LESSERCO", 48, "LEVEL:", color.by_name["green"])
        screen.blit(level_label, (self.cfg.board_size[0]+10, 20))
        level_value = self.res.font_render("LESSERCO", 48, str(self.level_num), color.by_name["green"])
        screen.blit(level_value, (self.cfg.board_size[0]+10, 60))

        points_label = self.res.font_render("LESSERCO", 48, "POINTS:", color.by_name["green"])
        screen.blit(points_label, (self.cfg.board_size[0]+10, 120))
        points_value = self.res.font_render("LESSERCO", 48, str(self.points), color.by_name["green"])
        screen.blit(points_value, (self.cfg.board_size[0]+10, 160))

        points_label = self.res.font_render("LESSERCO", 48, "DEATHS:", color.by_name["red"])
        screen.blit(points_label, (self.cfg.board_size[0]+10, 220))
        points_value = self.res.font_render("LESSERCO", 48, str(self.deaths), color.by_name["red"])
        screen.blit(points_value, (self.cfg.board_size[0]+10, 260))

        if self.stopped:
            dark = pygame.Surface(self.cfg.screen_resolution).convert_alpha()
            dark.fill((0,0,0,200))
            screen.blit(dark, (0,0))
            stopped_text = self.res.font_render("LESSERCO", 90, "THE GAME IS PAUSED", color.by_name["red"])
            screen.blit(stopped_text, (110,200))
            anykey_text = self.res.font_render("LESSERCO", 48, "Please press any key to start", color.by_name["red"])
            screen.blit(anykey_text, (160,270))
            arrows_text = self.res.font_render("LESSERCO", 48, "You are in center. Use arrows to move", color.by_name["red"])
            screen.blit(arrows_text, (110,350))
            avoid_text = self.res.font_render("LESSERCO", 48, "Avoid cars, director and sister", color.by_name["red"])
            screen.blit(avoid_text, (110,400))
            collect_text = self.res.font_render("LESSERCO", 48, "Collect dictionaries (stars)", color.by_name["red"])
            screen.blit(collect_text, (110,450))


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
