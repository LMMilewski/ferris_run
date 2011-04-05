import pygame
from pygame.locals import *

from config import *
from game_fsm import *
from resources import *

class Ferris:
    def __init__(self, cfg, res):
        self.cfg = cfg
        self.res = res

    def update(self, dt):
        pass

    def display(self, screen):
        pass

class FerrisRunGame(GameState):
    def __init__(self, cfg, res):
        self.cfg = cfg
        self.res = res

        self.__is_finished = False
        self.level_num = None # set in set_level called from init
        self.ferris = Ferris(cfg, res)

    def init(self, screen):
        self.set_level(1)

    def set_level(self, level_num):
        self.level_num = level_num
        self.res.music_play("level_background")
        self.res.sounds_play("level_start")

    def go_to_next_level(self):
        self.set_level(self.level_num + 1)

    def update(self, dt):
        self.ferris.update(dt)

    def process_event(self, event):
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                self.finish()
            if event.key == K_LEFT:
                pass
            if event.key == K_RIGHT:
                pass
            if event.key == K_UP:
                pass
            if event.key == K_DOWN:
                pass
            if event.key == K_1:
                self.res.sounds_play("level_start")
            if event.key == K_2:
                self.res.music_play("level_background")

    def display(self, screen):
        self.ferris.display(screen)

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
