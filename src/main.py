import pygame
from pygame.locals import *

import math
import random
import traffic_light, const

from config import *
from game_fsm import *
from resources import *
from sprite import *

from lane import Lane
from car import Car
from traffic_light import TrafficLight
from cop import Cop, CopSprite

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

def target_to_directions(position, target):
    """
    assuming you can go in X or Y direction, try to shorten larger of
    distances: distances in x, distances in y
    """
    if target == None:
       return (-1,0)
    else:
        target_dx = target[0] - position[0]
        target_dy = target[1] - position[1]
        horizontal_direction = DIR_LEFT if target_dx < 0 else DIR_RIGHT
        vertical_direction = DIR_UP if target_dy < 0 else DIR_DOWN
        if abs(target_dx) > abs(target_dy):
            return [horizontal_direction, vertical_direction, (horizontal_direction + 4) % 2, (vertical_direction + 4) % 2]
        else:
            return [vertical_direction, horizontal_direction, (vertical_direction + 4) % 2, (horizontal_direction + 4) % 2]


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


class BonusWithTimer:
    def __init__(self, cfg, res, command, undo_command, name, passive = False):
        """ if the bonus is passive (passive = True) then the bonus is never deactivated
        """
        self.cfg = cfg
        self.res = res
        self.command = command
        self.passive = passive
        self.undo_command = undo_command
        self.sprite = Sprite(name + "-mini", self.res, None, ORIGIN_TOP_LEFT)
        self.sprite_dark = Sprite(name + "-mini-dark", self.res, None, ORIGIN_TOP_LEFT)
        self.reset()
        self.type = "timer"

    def on_add(self):
        if self.passive:
            self.activate()

    def activate(self):
        if not self.active:
            self.active = True
            self.command()

    def deactivate(self):
        if self.passive:
            return
        self.finished = True
        self.active = False
        self.undo_command()
        self.time_left = 0
        if self.cfg.infinite_bonus:
            self.reset()

    def update(self, dt):
        if self.passive:
            return
        if self.active:
            self.time_left -= dt
            if self.time_left <= 0:
                self.deactivate()

    def reset(self):
        self.finished = False
        self.active = False
        if self.passive:
            self.time_left = "passive"
            return
        self.time_left = self.cfg.bonus_duration

class BonusWithCounter:
    def __init__(self, cfg, res, command, name):
        self.cfg = cfg
        self.res = res
        self.command = command
        self.sprite = Sprite(name + "-mini", self.res, None, ORIGIN_TOP_LEFT)
        self.sprite_dark = Sprite(name + "-mini-dark", self.res, None, ORIGIN_TOP_LEFT)
        self.reset()
        self.active = False
        self.type = "counter"

    def on_add(self):
        pass

    def activate(self):
        if self.count_left > 0:
            self.command()
            if not self.cfg.infinite_bonus:
                self.count_left -= 1
            if self.count_left == 0:
                self.finished = True

    def deactivate(self):
        pass

    def update(self, dt):
        pass

    def reset(self):
        self.count_left = self.cfg.bonus_count
        self.finished = False


class Ferris:
    def __init__(self, cfg, res):
        self.cfg = cfg
        self.res = res

        self.sprite = [ Sprite("ferris-left", self.res, 0.1),
                        Sprite("ferris-down", self.res, 0.1),
                        Sprite("ferris-right", self.res, 0.1),
                        Sprite("ferris-up", self.res, 0.1) ]
        self.speed = self.cfg.ferris_speed
        self.reset()
        self.seen_by_cop = False

    def update(self, dt, cars):
        self.sprite[self.direction].update(dt)
        lastX = self.position[0]
        lastY = self.position[1]
        speed = self.speed
        if self.seen_by_cop:
            speed *= self.cfg.cop_slowdown_multiplier
        self.position = get_next_position(self.cfg, self.position, self.direction, dt, speed)
        for car in cars:
            if aabb_collision(self.aabb(), car.aabb()):
                self.position = (lastX, lastY)
                if car.isInFront(self):
                    self.position = get_next_position(self.cfg, self.position, self.direction, dt, speed)
                return;

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

    def getPosition(self):
        return self.sprite[self.direction].getPosition(self.position)

    def getSize(self):
        return self.sprite[self.direction].getSize()

    def get_position(self):
        return self.position;

# should refactor? the code is the same as Ferris's and other guys
class Director:
    def __init__(self, cfg, res, ferris):
        self.cfg = cfg
        self.res = res
        self.ferris = ferris

        self.sprite = [ Sprite("director-left", self.res, 0.1),
                        Sprite("director-down", self.res, 0.1),
                        Sprite("director-right", self.res, 0.1),
                        Sprite("director-up", self.res, 0.1) ]
        self.direction = DIR_LEFT
        self.speed = self.cfg.director_speed
        self.position = (500,500)
        self.target = None
        self.flee = False

    def update(self, dt, objects):
        self.sprite[self.direction].update(dt)

        lastX = self.position[0]
        lastY = self.position[1]

        self.target = self.ferris.position
        if self.flee:
            self.target = (500, 500)
        else:
            self.target = self.ferris.position

        for direction in target_to_directions(self.position, self.target):
            valid = True
            prev_position = self.position
            self.position = get_next_position(self.cfg, self.position, direction, dt, self.speed)
            for object in objects:
                if aabb_collision(self.aabb(), object.aabb()):
                    valid = False
                    self.position = prev_position
                    break;
            if valid:
                self.direction = direction
                break

    def display(self, screen):
        self.sprite[self.direction].display(screen, self.position)

    def aabb(self):
        return self.sprite[self.direction].aabb(self.position)

    def getPosition(self):
        return self.sprite[self.direction].getPosition(self.position)

    def getSize(self):
        return self.sprite[self.direction].getSize()

class Sister:
    def __init__(self, cfg, res, ferris):
        self.cfg = cfg
        self.res = res
        self.ferris = ferris   
        self.sprite = [ Sprite("sister-left", self.res, 0.1),
                        Sprite("sister-down", self.res, 0.1),
                        Sprite("sister-right", self.res, 0.1),
                        Sprite("sister-up", self.res, 0.1) ]

        self.direction = DIR_LEFT
        self.speed = self.cfg.sister_speed
        self.position = (100,100)
        self.target = None
        self.flee = False

    def update(self, dt, objects):
        self.sprite[self.direction].update(dt)

        if self.flee:
            self.target = (100,100)
        else:
            if distance(self.ferris.position, self.position) < 70:
                self.target = self.ferris.position
            else:
                ferris_dir = direction_to_vector(self.ferris.direction)
                self.target = self.ferris.position[0] + ferris_dir[0] * 80, self.ferris.position[1] + ferris_dir[1] * 80

        for direction in target_to_directions(self.position, self.target):
            if direction == (self.direction + 2) % 4: # can't reverse direction
                continue
            valid = True
            prev_position = self.position
            self.position = get_next_position(self.cfg, self.position, direction, dt, self.speed)
            for object in objects:
                if aabb_collision(self.aabb(), object.aabb()):
                    valid = False
                    self.position = prev_position
                    break;
            if valid:
                self.direction = direction
                break

    def display(self, screen):
        self.sprite[self.direction].display(screen, self.position)

    def aabb(self):
        return self.sprite[self.direction].aabb(self.position)

    def getPosition(self):
        return self.sprite[self.direction].getPosition(self.position)

    def getSize(self):
        return self.sprite[self.direction].getSize()

class Register:
    def __init__(self, cfg, res, initial_position = None):
        self.cfg = cfg
        self.res = res
        self.sprite = Sprite("register", self.res, 0.1)

        if initial_position != None:
            self.position = initial_position
        else:
            while True:
                position = random.randint(20,580), random.randint(20,580)
                if position[0] < 20 or position[1] < 20:
                    continue
                if 160 <= position[0] and position[0] <= 220:
                    continue
                if 380 <= position[0] and position[0] <= 440:
                    continue
                if 160 <= position[1] and position[1] <= 220:
                    continue
                if 380 <= position[1] and position[1] <= 440:
                    continue
                self.position = position
                break

    def update(self, dt):
        self.sprite.update(dt)

    def display(self, screen):
        self.sprite.display(screen, self.position)

    def aabb(self):
        return self.sprite.aabb(self.position)

class MainMenu(GameState):
    def __init__(self, cfg, res):
        self.cfg = cfg
        self.res = res  
        self.logo = Sprite("logo", self.res, None, ORIGIN_TOP_LEFT)
        self.sprites = [Sprite("sister-right", res, 0.1), Sprite("director-right", res, 0.1), Sprite("ferris-right", res, 0.1)]
        self.positions = [[0, 90], [30, 90], [100, 90]]
        self.bubble = Sprite("SpeechBubble", self.res)
        self.startGame = [Sprite("startgame1", self.res, None, ORIGIN_TOP_LEFT), Sprite("startgame0", self.res, None, ORIGIN_TOP_LEFT)]
        self.highscores = [Sprite("highscores1", self.res, None, ORIGIN_TOP_LEFT), Sprite("highscores0", self.res, None, ORIGIN_TOP_LEFT)]
        self.menuPosition = 0
        self.finished = False
      
    def update(self, dt):
        for person in self.sprites:
            person.update(dt)
        for pos in self.positions:
            pos[0] += 50 * dt
            if pos[0] > self.cfg.resolution[0]:
                pos[0] = 0
      
    def display(self, screen):
        screen.fill((239, 239, 239))
        self.logo.display(screen, (0,100))
        for i in range(0, len(self.sprites)):
            self.sprites[i].display(screen, self.positions[i])
        if self.positions[1][0] > 100 and self.positions[1][0] < 300:
            self.bubble.display(screen, (self.positions[1][0] + 40, 30))
            
        self.startGame[self.menuPosition].display(screen, (300, 300))
        self.highscores[1 - self.menuPosition].display(screen, (300, 350))
            
    def next_state(self):
        if self.menuPosition == 0:
            return FerrisRunGame(self.cfg, self.res)    
        else:
            return Highscores(self.cfg, self.res)
                    
            
    def process_event(self, event):
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                self.finish()
            if event.key == K_UP:
                self.menuPosition = (self.menuPosition + 1) % 2
            if event.key == K_DOWN:
                self.menuPosition = (self.menuPosition + 1) % 2           
            if event.key == K_RETURN:
                self.finished = True
                
    def is_finished(self):
        return self.finished                


class Highscores(GameState):
    def __init__(self, cfg, res):
        self.cfg = cfg
        self.res = res  
        self.finished = False
        self.logo = Sprite("highscoreslogo", self.res, None, ORIGIN_TOP_LEFT)
        self.highscores = self.res.get_highscores()            
        
    def update(self, dt):
        pass
      
    def display(self, screen):
        screen.fill((239, 239, 239))
        self.logo.display(screen, (0,0))
        
        position = 180
        i = 1
        label = self.res.font_render("LESSERCO", 36, "name   scores   deaths", color.by_name["black"])
        screen.blit(label, (300, 150))    
        for entry in self.highscores:
            label = self.res.font_render("LESSERCO", 36, str(i) + "." + entry["name"] + "\t" + entry["points"] + "\t" + entry["deaths"], color.by_name["black"])
            screen.blit(label, (300, position))    
            position += 30
            i += 1    
            
    def next_state(self):
        return MainMenu(self.cfg, self.res)    
                    
            
    def process_event(self, event):
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                self.finished = True
                      
    def is_finished(self):
        return self.finished    

class FerrisRunGame(GameState):
    def __init__(self, cfg, res):
        self.cfg = cfg
        self.res = res

        self.__is_finished = False
        self.level_num = None # set in set_level called from init
        self.register = Register(cfg, res, (350, 350))

        self.background = Sprite("background", self.res, None, ORIGIN_TOP_LEFT)
        self.hud = Sprite("hud", self.res, None, ORIGIN_TOP_LEFT)

        self.points = 0
        self.deaths = 0
        self.bonuses = []
        self.blood_sprite = Sprite("blood", self.res)
        self.blood_positions = []
        self.remote_gather = False

        self.stopped = True # the game is not playing right now (characters don't move etc)

        self.answer = Sprite("answer", self.res)

        self.trafficLights = [TrafficLight(traffic_light.YELLOW_BEFORE_GREEN, 160, 160),
                              TrafficLight(traffic_light.YELLOW_BEFORE_GREEN, 380, 160),
                              TrafficLight(traffic_light.YELLOW_BEFORE_GREEN, 220, 380),
                              TrafficLight(traffic_light.YELLOW_BEFORE_GREEN, 440, 380),
                              TrafficLight(traffic_light.YELLOW_BEFORE_RED, 160, 220),
                              TrafficLight(traffic_light.YELLOW_BEFORE_RED, 160, 440),
                              TrafficLight(traffic_light.YELLOW_BEFORE_RED, 380, 160),
                              TrafficLight(traffic_light.YELLOW_BEFORE_RED, 380, 380)]
        self.trafficLights[0].setPosition(610, 300)
        self.trafficLights[1].setPosition(390, 160)
        self.trafficLights[2].setPosition(220, 300)
        self.trafficLights[3].setPosition(440, 300)
        self.trafficLights[4].setPosition(140, 440)
        self.trafficLights[6].setPosition(360, 160)
        self.trafficLights[7].setPosition(360, 380)

        crossings =  [(160, 160, 80, 80), (380, 160, 80, 80), (160, 380, 80, 80), (380, 380, 80, 80)]

        self.lanes = [Lane(50, [self.trafficLights[0], self.trafficLights[1]], const.RIGHT, 3, (0, 160), [(140, 140, 80, 80), (380, 140, 80, 80)], self.cfg, res),
                 Lane(100, [self.trafficLights[0], self.trafficLights[1]], const.RIGHT, 3, (0, 181), [(140, 140, 80, 80), (380, 140, 80, 80)], self.cfg, res),
                 Lane(70, [self.trafficLights[0], self.trafficLights[1]], const.RIGHT, 3, (0, 202), [(140, 140, 80, 80), (380, 140, 80, 80)], self.cfg, res),
                 Lane(60, [self.trafficLights[2], self.trafficLights[3]], const.LEFT, 3, (self.cfg.board_size[0] - 40, 380), [(140, 380, 80, 80), (380, 380, 80, 80)], self.cfg, res),
                 Lane(120, [self.trafficLights[2], self.trafficLights[3]], const.LEFT, 3, (self.cfg.board_size[0] - 40, 401), [(140, 380, 80, 80), (380, 380, 80, 80)], self.cfg, res),
                 Lane(80, [self.trafficLights[2], self.trafficLights[3]], const.LEFT, 3, (self.cfg.board_size[0] - 40, 422), [(140, 380, 80, 80), (380, 380, 80, 80)], self.cfg, res),
                 Lane(40, [self.trafficLights[4], self.trafficLights[5]], const.UP, 3, (162, self.cfg.board_size[1] - 40), [(140, 140, 80, 80), (160, 380, 80, 80)], self.cfg, res),
                 Lane(80, [self.trafficLights[4], self.trafficLights[5]], const.UP, 3, (182, self.cfg.board_size[1] - 40), [(140, 140, 80, 80), (160, 380, 80, 80)], self.cfg, res),
                 Lane(60, [self.trafficLights[4], self.trafficLights[5]], const.UP, 3, (203, self.cfg.board_size[1] - 40), [(140, 140, 80, 80), (160, 380, 80, 80)], self.cfg, res),
                 Lane(60, [self.trafficLights[6], self.trafficLights[7]], const.DOWN, 3, (381, 0), [(380, 140, 80, 80), (380, 360, 80, 80)], self.cfg, res),
                 Lane(100, [self.trafficLights[6], self.trafficLights[7]], const.DOWN, 3, (403, 0), [(380, 140, 80, 80), (380, 360, 80, 80)], self.cfg, res),
                 Lane(80, [self.trafficLights[6], self.trafficLights[7]], const.DOWN, 3, (423, 0), [(380, 140, 80, 80), (380, 360, 80, 80)], self.cfg, res)]
        self.cars = []
        for lane in self.lanes:
            self.cars += lane.getCars()

        self.allsprites = pygame.sprite.RenderPlain([self.trafficLights[0]])

        self.time = 0
        self.lasttime = 0
        self.timeoffset = [10, 3]
        self.currentOffset = 1
        self.last_keys = []
        self.cops = [Cop(260, 170, 390, 170)]
        self.cop_sprites = pygame.sprite.Group()
        for cop in self.cops:
            self.cop_sprites.add(cop.GetSprite());

    def init(self, screen):
        self.bullet_time = False
        self.rich_mode = False
        self.ferris = Ferris(self.cfg, self.res)
        self.set_level(1)
        self.define_possible_bonuses()

    def define_possible_bonuses(self):
        self.possible_bonuses = [
            [ BonusWithTimer(self.cfg, self.res, self.ferris.set_speed_fast, self.ferris.set_speed_normal, "bonus-speed"),
              BonusWithTimer(self.cfg, self.res, self.bullet_time_on, self.bullet_time_off, "bonus-slow"),
              BonusWithTimer(self.cfg, self.res, self.rich_mode_on, self.rich_mode_off, "bonus-rich"),
              BonusWithTimer(self.cfg, self.res, self.enemies_flee_on, self.enemies_flee_off, "bonus-enemies-flee"),
              BonusWithTimer(self.cfg, self.res, self.lights_crash_on, self.lights_crash_off, "bonus-lights"), ],
            [ BonusWithCounter(self.cfg, self.res, self.pick_register, "bonus-pick"),
              BonusWithTimer(self.cfg, self.res, self.remote_gather_on, self.remote_gather_off, "bonus-remote-gather", True), ]
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
        self.enemies = [self.director, self.sister] + self.cars
        self.stopped = True

    def go_to_next_level(self):
        self.blood_positions = []
        self.set_level(self.level_num + 1)
        for bonus in self.bonuses:
            bonus.reset()

    def die(self):
        self.blood_positions.append(self.ferris.position)
        self.res.sounds_play("die")
        self.deaths += 1
        self.reset_level()

    def update(self, dt):
        self.dt = dt

        if self.bullet_time:
            dt *= self.cfg.bullet_slowdown_factor

        if self.stopped:
            return

        self.background.update(dt)

        for car in self.cars:
            car.update(dt, self.cars, [self.director, self.sister])

        no_of_cops_seeing_ferris = 0;
        for cop in self.cops:
            no_of_cops_seeing_ferris += cop.update(dt, self.ferris.get_position());
        self.ferris.seen_by_cop = no_of_cops_seeing_ferris > 0

        self.hud.update(dt)

        # update all objects
        if self.bullet_time:
            self.ferris.update(dt / self.cfg.bullet_slowdown_factor, self.cars)
        else:
            self.ferris.update(dt, self.cars)
        self.director.update(dt, self.cars)
        self.sister.update(dt, self.cars)
        self.register.update(dt)
        for bonus in self.bonuses:
            if self.bullet_time:
                bonus.update(dt / self.cfg.bullet_slowdown_factor)
            else:
                bonus.update(dt)


        # check collision with register
        if self.collision_with_register():
           self.res.sounds_play("collect")
           self.register = Register(self.cfg, self.res)

           self.points += 100 * (self.cfg.rich_mode_multiplier if self.rich_mode else 1)

           self.registers_left -= 1
           if self.registers_left <= 0:
               self.go_to_next_level()
               return

        # check collision with enemies
        if not self.cfg.godmode:
            #enemies = [self.director, self.sister]
            for enemy in self.enemies:
                if aabb_collision(self.ferris.aabb(), enemy.aabb()):
                    self.die()
                    return


        self.time += dt
        if self.time > self.lasttime + self.timeoffset[self.currentOffset]:
            self.lasttime = self.time
            self.currentOffset = 1 - self.currentOffset
            for light in self.trafficLights:
                light.changeState()
            for lane in self.lanes:
                lane.changeState()

        self.allsprites.update()

    def collision_with_register(self):
        if self.remote_gather:
            return distance(self.ferris.position, self.register.position) < self.cfg.remote_gather_radius
        else:
            return aabb_collision(self.ferris.aabb(), self.register.aabb())

    def bullet_time_on(self):
        self.bullet_time = True

    def bullet_time_off(self):
        self.bullet_time = False

    def rich_mode_on(self):
        self.rich_mode = True

    def rich_mode_off(self):
        self.rich_mode = False

    def enemies_flee_on(self):
        self.director.flee = True
        self.sister.flee = True

    def enemies_flee_off(self):
        self.director.flee = False
        self.sister.flee = False

    def lights_crash_on(self):
        self.lasttime = self.time
        self.currentOffset = 1
        for lane in self.lanes:
            lane.stop()

    def lights_crash_off(self):
        self.lasttime = self.time
        self.currentOffset = 1
        for lane in self.lanes:
            lane.reset()

    def remote_gather_on(self):
        self.remote_gather = True

    def remote_gather_off(self): # this is passive, always active
        pass

    def pick_register(self):
        self.res.sounds_play("collect")
        self.register = Register(self.cfg, self.res)
        self.points += 100 * (self.cfg.rich_mode_multiplier if self.rich_mode else 1)
        self.registers_left -= 1
        if self.registers_left <= 0:
            self.go_to_next_level()

    def process_event(self, event):
        if event.type == KEYDOWN:
            self.last_keys.append(event.key)
            self.last_keys = self.last_keys[-100:]
            if self.last_keys[-len(self.cfg.cheat_sequence):] == self.cfg.cheat_sequence:
                self.cfg.cheat_mode = True
            if self.cfg.cheat_mode:
                if self.last_keys[-len(self.cfg.godmode_sequence1):] == self.cfg.godmode_sequence1:
                    self.cfg.godmode = True
                if self.last_keys[-len(self.cfg.godmode_sequence2):] == self.cfg.godmode_sequence2:
                    self.cfg.godmode = True
                if self.last_keys[-len(self.cfg.infinite_bonus_sequence):] == self.cfg.infinite_bonus_sequence:
                    self.cfg.infinite_bonus = True
                    for bonus in self.bonuses:
                        bonus.reset()
                if self.last_keys[-len(self.cfg.answer_sequence):] == self.cfg.answer_sequence:
                    self.cfg.answer = True
            if event.key == K_p:
                self.stopped = True
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
            if event.key == K_1:
                if len(self.bonuses) > 0:
                    self.bonuses[0].activate()
            if event.key == K_2:
                if len(self.bonuses) > 1:
                    self.bonuses[1].activate()
            if event.key == K_3:
                if len(self.bonuses) > 2:
                      self.bonuses[2].activate()
            if event.key == K_4:
                if len(self.bonuses) > 3:
                    self.bonuses[3].activate()
            if event.key == K_5:
                if len(self.bonuses) > 4:
                    self.bonuses[4].activate()
            if self.cfg.cheat_mode:
                if event.key == K_7:
                    self.bonuses = self.possible_bonuses[0]
                    for bonus in self.bonuses:
                        bonus.on_add()
                if event.key == K_8:
                    self.bonuses = self.possible_bonuses[1]
                    for bonus in self.bonuses:
                        bonus.on_add()
                if event.key == K_9:
                    self.go_to_next_level()
                if event.key == K_0:
                    self.cfg.print_fps = not self.cfg.print_fps

    def display(self, screen):
        self.background.display(screen, (0,0))

        for blood_position in self.blood_positions:
            self.blood_sprite.display(screen, blood_position)

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

            if bonus.type == "timer":
                text_time_left = self.res.font_render("LESSERCO", 36, str(bonus.time_left)+"s", color.by_name["red"])
            elif bonus.type == "counter":
                text_time_left = self.res.font_render("LESSERCO", 36, " x " + str(bonus.count_left), color.by_name["red"])
            screen.blit(text_time_left, (menu_x + 60, bonus_y))

            bonus_y += 50

        self.cop_sprites.update();
        self.cop_sprites.draw(screen);

        self.allsprites.draw(screen)
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

        if self.cfg.answer:
            self.answer.display(screen, (350,350))

        if self.cfg.print_fps:
            self.display_key_value(screen, (0,0), "DT / FPS",  str(self.dt) + " / " + str(int(1.0/self.dt)))

        if self.cfg.cheat_mode:
            self.display_key_value(screen, (300, 550), "!!! CHEATER !!!", "")

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
    fsm.set_state(MainMenu(cfg,res))
    #fsm.set_state(FerrisRunGame(cfg,res))
    pygame.display.set_caption(cfg.app_name)
    pygame.mouse.set_visible(not cfg.fullscreen)
    fsm.run()
