""" Proviedes global game informations

Store there all configuration variables instead of hardcoding them in
the game code.

It provides public access to its fields, so:
  - you should mostly read these variables
  - modify them only if you have to. Do it in organized way or your
    game will work unexpectedly
"""
import os, sys
from pygame.locals import *

class Config:
    def __init__(self):
        ## general stuff
        self.sound = not "--nosounds" in sys.argv
        self.music = not "--nomusic" in sys.argv
        self.resolution = 800,600 # in this resolution the game is blited onto Surface
        self.screen_resolution = 800,600 # just before swap buffers the screen is scaled to this resolution
        self.fullscreen = "--fullscreen" in sys.argv
        self.fullscreen = True
        self.fps_limit = 60
        self.app_name = "Ferris Run"

        self.print_fps = False

        ## paths
        base_path = os.path.abspath(os.path.dirname(sys.argv[0]))
        self.__path={}
        for data_type in ("gfx", "sounds", "music", "font", "highscores"):
            self.__path[data_type] = os.path.join(base_path, data_type)

        self.highscores_path =  os.path.join(base_path, "highscores")
        # you can't inline __add_path_getter method because in python
        # closures are created by function calls
        for k, v in self.__path.items():
            self.__add_path_getter(k,v)

        ### game specyfic options
        self.game_speed_multipliers = [0, 0.8, 0.9, 0.9, 1.0, 1.0, 1.1, 1.15, 1.2, 1.4]
        self.ferris_speed = 100
        self.ferris_speed_fast = 200
        self.cop_slowdown_multiplier = 0.5
        self.director_speed = 60
        self.sister_speed = 70
        self.car_speed = 120
        self.board_size = 600,600
        self.registers_per_level = 9
        self.bonus_duration = 10
        self.bonus_count = 2
        self.remote_gather_radius = 100
        self.bullet_slowdown_factor = 0.5
        self.rich_mode_multiplier = 2
        self.cheat_mode = '--cheatmode' in sys.argv
        self.cheat_sequence = [K_UP, K_UP, K_DOWN, K_DOWN, K_LEFT, K_RIGHT, K_LEFT, K_RIGHT, K_a, K_b]
        self.godmode = False
        self.godmode_sequence1 = [K_t, K_e, K_r, K_r, K_i, K_b, K_l, K_e, K_t, K_e, K_r, K_r, K_i, K_b, K_l, K_e, K_d, K_a, K_m, K_a, K_g, K_e] # + cheat_mode enabled
        self.godmode_sequence2 = [K_g, K_o, K_d] # + cheat_mode enabled
        self.infinite_bonus = False
        self.infinite_bonus_sequence = [K_d, K_n, K_k, K_r, K_o, K_z] # + cheat_mode enabled
        self.answer = False
        self.answer_sequence = [K_a, K_n, K_s, K_w, K_e, K_r, K_t, K_o, K_l, K_i, K_f, K_e, K_u, K_n, K_i, K_v, K_e, K_r, K_s, K_e, K_a, K_n, K_d, K_e, K_v, K_e, K_r, K_y, K_t, K_h, K_i, K_n, K_g] # + cheat_mode enabled
        self.highscore_entries = 10
        self.highscore_delimiter = "-"
        self.highscore_entry_delimiter = "|"
        self.nick_length = 6

    def __add_path_getter(self, k, v):
            setattr(Config,
                    k + "_path",
                    lambda self_, fname: os.path.join(v, fname))
