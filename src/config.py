""" Proviedes global game informations

Store there all configuration variables instead of hardcoding them in
the game code.

It provides public access to its fields, so:
  - you should mostly read these variables
  - modify them only if you have to. Do it in organized way or your
    game will work unexpectedly
"""
import os, sys

class Config:
    def __init__(self):
        ## general stuff
        self.sound = not "--nosounds" in sys.argv
        self.music = not "--nomusic" in sys.argv
        self.resolution = 800,600 # in this resolution the game is blited onto Surface
        self.screen_resolution = 800,600 # just before swap buffers the screen is scaled to this resolution
        self.fullscreen = "--fullscreen" in sys.argv
        self.fps_limit = 60

        self.print_fps = False

        ## paths
        base_path = os.path.abspath(os.path.dirname(sys.argv[0]))
        self.__path={}
        for data_type in ("gfx", "sounds", "music", "font"):
            self.__path[data_type] = os.path.join(base_path, data_type)

        # you can't inline __add_path_getter method because in python
        # closures are create by function calls
        for k, v in self.__path.items():
            self.__add_path_getter(k,v)
        ### game specyfic options
        self.ferris_speed = 100
        self.ferris_speed_fast = 200
        self.ferris_speed_cop = 50;
        self.director_speed = 60
        self.sister_speed = 70
        self.car_speed = 120
        self.board_size = 600,600
        self.registers_per_level = 9
        self.bonus_duration = 10
        self.bullet_slowdown_factor = 0.5
        self.rich_mode_multiplier = 2

    def __add_path_getter(self, k, v):
            setattr(Config,
                    k + "_path",
                    lambda self_, fname: os.path.join(v, fname))
