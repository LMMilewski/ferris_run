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


class Bonus:
    def __init__(self, cfg, res, command, undo_command, name):
        self.cfg = cfg
        self.res = res
        self.command = command
        self.undo_command = undo_command
        self.sprite = Sprite(name + "-mini", self.res, None, ORIGIN_TOP_LEFT)
        self.sprite_dark = Sprite(name + "-mini-dark", self.res, None, ORIGIN_TOP_LEFT)
        self.reset()

    def activate(self):
        self.active = True
        self.command()

    def deactivate(self):
        self.finished = True
        self.active = False
        self.undo_command()
        self.time_left = 0

    def update(self, dt):
        if self.active:
            self.time_left -= dt
            if self.time_left <= 0:
                self.deactivate()

    def reset(self):
        self.active = False
        self.time_left = self.cfg.bonus_duration
        self.finished = False

class Ferris:
    def __init__(self, cfg, res):
        self.cfg = cfg
        self.res = res

        self.sprite = [ Sprite("ferris-left", self.res, 0.5),
                        Sprite("ferris-down", self.res, 0.5),
                        Sprite("ferris-right", self.res, 0.5),
                        Sprite("ferris-up", self.res, 0.5) ]
        self.speed = self.cfg.ferris_speed
        self.reset()

    def update(self, dt):
        self.sprite[self.direction].update(dt)
        self.position = get_next_position(self.cfg, self.position, self.direction, dt, self.speed)

    def display(self, screen):
        self.sprite[self.direction].display(screen, self.position)

    def aabb(self):
        return self.sprite[self.direction].aabb(self.position)

    def reset(self):
        self.position = (300,300)
        self.direction = DIR_LEFT

    def set_speed_normal(self):
        self.speed = self.cfg.ferris_speed

    def set_speed_fast(self):
        self.speed = self.cfg.ferris_speed_fast

# should refactor? the code is the same as Ferris's and other guys
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
        self.bonuses = []

        self.stopped = True # the game is not playing right now (characters don't move etc)

    def init(self, screen):
        self.ferris = Ferris(self.cfg, self.res)
        self.set_level(1)
        self.define_possible_bonuses()

    def define_possible_bonuses(self):
        self.possible_bonuses = [
            [ Bonus(self.cfg, self.res, self.ferris.set_speed_fast, self.ferris.set_speed_normal, "bonus-speed") ],
            [ ]
            ]

    def set_level(self, level_num):
        self.level_num = level_num
        self.reset_level()
        self.res.music_play("level_background")
        self.res.sounds_play("level_start")
        self.registers_left = self.cfg.registers_per_level

    def reset_level(self):
        self.ferris.reset()
        self.director = Director(self.cfg, self.res, self.ferris)
        self.sister = Sister(self.cfg, self.res, self.ferris)
        self.stopped = True

    def go_to_next_level(self):
        self.set_level(self.level_num + 1)
        for bonus in self.bonuses:
            bonus.deactivate()
            bonus.reset()

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
        for bonus in self.bonuses:
            bonus.update(dt)
        for car in self.cars:
            car.update(dt)

        # check collision with register
        if aabb_collision(self.ferris.aabb(), self.register.aabb()):
            self.res.sounds_play("collect")
            self.register = Register(self.cfg, self.res, self.random)
            self.points += 100
            self.registers_left -= 1
            if self.registers_left <= 0:
                self.go_to_next_level()
                return

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
                if len(self.bonuses) > 0:
                    self.bonuses[0].activate()
            if event.key == K_2:
                pass
            if event.key == K_3:
                pass
            if event.key == K_4:
                pass
            if event.key == K_5:
                pass
            if event.key == K_7:
                self.bonuses = self.possible_bonuses[0]
            if event.key == K_8:
                self.bonuses = self.possible_bonuses[1]
            if event.key == K_9:
                self.go_to_next_level()
            if event.key ==K_0:
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

        # hud
        menu_x = self.cfg.board_size[0] + 10
        self.display_key_value(screen, (menu_x, 20), "LEVEL", self.level_num)
        self.display_key_value(screen, (menu_x, 70), "POINTS", self.points)
        self.display_key_value(screen, (menu_x, 130), "DEATHS", self.deaths)
        self.display_key_value(screen, (menu_x, 180), "REGISTERS", self.registers_left)

        # bonuses
        bonus_y = 300
        if self.bonuses != []:
            self.display_key_value(screen, (menu_x, bonus_y-40), "BONUSES")
        for bonus in self.bonuses:
            if bonus.active:
                pygame.draw.rect(screen, color.by_name["blue"], (self.cfg.board_size[0]+10-3, bonus_y-1, 46, 43), 3)
            if bonus.finished:
                bonus.sprite_dark.display(screen, (self.cfg.board_size[0]+10, bonus_y))
            else:
                bonus.sprite.display(screen, (self.cfg.board_size[0]+10, bonus_y))
            text_time_left = self.res.font_render("LESSERCO", 36, str(bonus.time_left), color.by_name["red"])
            screen.blit(text_time_left, (menu_x + 60, bonus_y))
            bonus_y += 50

        # pause menu
        if self.stopped:
            dark = pygame.Surface(self.cfg.screen_resolution).convert_alpha()
            dark.fill((0,0,0,200))
            screen.blit(dark, (0,0))
            stopped_text = self.res.font_render("LESSERCO", 90, "THE GAME IS PAUSED", color.by_name["red"])
            screen.blit(stopped_text, (110,200))
            anykey_text = self.res.font_render("LESSERCO", 36, "Please press any key to start", color.by_name["red"])
            screen.blit(anykey_text, (160,270))
            arrows_text = self.res.font_render("LESSERCO", 36, "You are in center. Use arrows to move", color.by_name["red"])
            screen.blit(arrows_text, (110,350))
            avoid_text = self.res.font_render("LESSERCO", 36, "Avoid cars, director and sister", color.by_name["red"])
            screen.blit(avoid_text, (110,400))
            collect_text = self.res.font_render("LESSERCO", 36, "Collect dictionaries (stars)", color.by_name["red"])
            screen.blit(collect_text, (110,450))

    def display_key_value(self, screen, position, key, value = ""):
        label = self.res.font_render("LESSERCO", 36, str(key), color.by_name["red"])
        screen.blit(label, (position[0], position[1]))
        value = self.res.font_render("LESSERCO", 36, str(value), color.by_name["red"])
        screen.blit(value, (position[0]+130, position[1]))

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
