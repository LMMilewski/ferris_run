import pygame
from pygame.locals import *

from config import *
from game_fsm import *
from resources import *
from sprite import *

class ChooseUpgradeWindow(GameState):
    def __init__(self, cfg, res, next_state, bonus0, bonus1):
        self.cfg = cfg
        self.res = res
        self.__is_finished = False
        self.__next_state = next_state
        self.__bonus = [bonus0, bonus1]
        self.__choice = 0

    def init(self, screen):
        pass

    def update(self, dt):
        pass

    def process_event(self, event):
        if event.type == KEYDOWN:
            if event.key == K_1:
                self.__choice = 0
                self.finish()
            elif event.key == K_2:
                self.__choice = 1
                self.finish()

    def display(self, screen):
        screen.fill(color.by_name["black"])
        title_text = self.res.font_render("LESSERCO", 90, "Level is clear!", color.by_name["red"])
        screen.blit(title_text, (200, 20))

        choose_text = self.res.font_render("LESSERCO", 36, "Choose one of these two upgrades", color.by_name["red"])
        screen.blit(choose_text, (20, 120))
        keys_text = self.res.font_render("LESSERCO", 36, "Use keys", color.by_name["red"])
        screen.blit(keys_text, (20, 430))
        one_text = self.res.font_render("LESSERCO", 36, "'1' (numeric one) for left bonus", color.by_name["red"])
        screen.blit(one_text, (100, 490))
        two_text = self.res.font_render("LESSERCO", 36, "'2' (numeric two) for right bonus", color.by_name["red"])
        screen.blit(two_text, (100, 530))

        pygame.draw.rect(screen, color.by_name["blue"], (20, 200, 360, 200), 3)
        pygame.draw.rect(screen, color.by_name["blue"], (420, 200, 360, 200), 3)

        self.__bonus[0].sprite.display(screen, (180, 220))
        self.__bonus[1].sprite.display(screen, (580, 220))

        bonus0_description = self.res.font_render("LESSERCO", 24, self.__bonus[0].description, color.by_name["red"])
        screen.blit(bonus0_description, (30, 310))
        bonus1_description = self.res.font_render("LESSERCO", 24, self.__bonus[1].description, color.by_name["red"])
        screen.blit(bonus1_description, (430, 310))

    def finish(self):
        if self.is_finished():
            return
        self.__next_state.add_upgrade(self.__bonus[self.__choice])
        self.__is_finished = True

    def is_finished(self):
        return self.__is_finished

    def next_state(self):
        return self.__next_state
