""" Providesorganized way to switch states (i.e. menu, intro, cutscene, level, ...)

To add new state to the game create new class derived from
GameState. You can define how to render/update the state

"""

import pygame
from pygame.locals import *
import config


class GameState:
    def __init__(self):
        pass

    def init(self, screen):
        pass

    def update(self, dt):
        pass

    def process_event(self, event):
        pass

    def display(self, screen):
        pass

    def finish(self):
        pass

    def is_finished(self):
        return False

    def next_state(self):
        return null_game_state

null_game_state = GameState()



class GameFsm:
    def __init__(self, cfg):
        self.is_finished = False # if true the main loop will be finished
        self.current_state = null_game_state # which state is executed now
        self.clock = pygame.time.Clock()
        self.cfg = cfg
        self.__init_pygame()

    def __init_pygame(self):
        pygame.mixer.pre_init(11025, -16, 2, 256)
        flags = 0
        if self.cfg.fullscreen:
            flags |= pygame.FULLSCREEN
        self.video_buffer = pygame.display.set_mode(self.cfg.screen_resolution, flags)
        self.screen = pygame.Surface(self.cfg.resolution).convert_alpha()
        pygame.init()

    def set_state(self, new_state):
        """ Finish previous state and set current state as new_state """
        self.current_state.finish()
        self.current_state = new_state
        self.current_state.init(self.screen)

    def finish(self):
        """ Shut down the GameFsm """
        self.set_state(null_game_state)
        self.is_finished = True

    def __process_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.finish();
            else:
                self.current_state.process_event(event)

    def run(self):
        """ Main loop. Updates current state, processes events, renders the scene

        Should be run after current state is set with set_state

        If the state finishes (is_finished returns True) then it is
        not allowed to do any actions (should do nothing)
        """
        while not self.is_finished:
            dt = self.clock.tick(self.cfg.fps_limit) * 0.001
            self.__process_events()
            if self.current_state.is_finished():
                if self.current_state.next_state() == null_game_state:
                    self.finish()
                else:
                    self.set_state(self.current_state.next_state())
                continue
            self.current_state.update(dt)

            self.current_state.display(self.screen)
            if (self.cfg.resolution != self.cfg.screen_resolution):
                pygame.transform.scale(self.screen, self.cfg.screen_resolution, self.video_buffer)
            else:
                self.video_buffer.blit(self.screen, (0,0))
            pygame.display.flip()
