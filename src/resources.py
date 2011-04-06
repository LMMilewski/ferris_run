""" Basic resource manager

To add new resources to your game put definitions in load_* methods

"""

import os
import pygame
from pygame.locals import *

import color

class Resources:
    """ Collects all resources in one class
    """
    def __init__(self, cfg):
        self.cfg = cfg
        self.sounds    = {}
        self.music     = {}
        self.font      = {}
        self.animation = {}

    def load_all(self):
        if self.cfg.sound:
            self.load_sound_files()
        if self.cfg.music:
            self.load_music_files()
        self.load_animation_files()
        self.load_font_files()
        return self

    ## define resources you want to use

    def load_sound_files(self):
        # add filename without extension here (i.e. 'cha-ching' will
        # load 'cha-ching.ogg' file)
        files = ["level_start",
                 "collect",
                 "die"]
        for file in files:
            self.load_sound_file(file)

    def load_music_files(self):
        # add filename without extension here (i.e. 'background' will
        # load 'background.ogg' file)
        files = ["level_background"]
        for file in files:
            self.load_music_file(file)

    def load_animation_files(self):
        # add filename without extension here (i.e. 'bg' will
        # load 'bg.png' file)
        files = ["background",
                 "hud",
                 "ferris-left",
                 "director-left",
                 "sister-left",
                 "register",
                 "car-left-white",
                 "bonus-speed-mini",
                 "bonus-speed-mini-dark",
                 "bonus-slow-mini",
                 "bonus-slow-mini-dark",
                 "bonus-rich-mini",
                 "bonus-rich-mini-dark"]
        for file in files:
            self.load_animation_file(file)

        # use __map_animation_frames to apply a function to every
        # frame in an animation here
        # i.e.
        # self.__map_animation_frames("orig_anim", "dest_anim",  self.__rotate_image(90))
        # will rotate it 90 degrees counter-clockwise
        self.__map_animation_frames("ferris-left", "ferris-down",  self.__rotate_image(90))
        self.__map_animation_frames("ferris-left", "ferris-right", self.__rotate_image(180))
        self.__map_animation_frames("ferris-left", "ferris-up",    self.__rotate_image(270))

        self.__map_animation_frames("director-left", "director-down",  self.__rotate_image(90))
        self.__map_animation_frames("director-left", "director-right", self.__rotate_image(180))
        self.__map_animation_frames("director-left", "director-up",    self.__rotate_image(270))

        self.__map_animation_frames("sister-left", "sister-down",  self.__rotate_image(90))
        self.__map_animation_frames("sister-left", "sister-right", self.__rotate_image(180))
        self.__map_animation_frames("sister-left", "sister-up",    self.__rotate_image(270))

        self.__map_animation_frames("car-left-white", "car-down-white",  self.__rotate_image(90))
        self.__map_animation_frames("car-left-white", "car-right-white", self.__rotate_image(180))
        self.__map_animation_frames("car-left-white", "car-up-white",    self.__rotate_image(270))

        self.__blend_animation_with_color("car-left-white", "car-left-red", color.by_name["red"])
        self.__blend_animation_with_color("car-down-white", "car-down-red", color.by_name["red"])
        self.__blend_animation_with_color("car-right-white", "car-right-red", color.by_name["red"])
        self.__blend_animation_with_color("car-up-white", "car-up-red", color.by_name["red"])

        self.__blend_animation_with_color("car-left-white", "car-left-blue", color.by_name["blue"])
        self.__blend_animation_with_color("car-down-white", "car-down-blue", color.by_name["blue"])
        self.__blend_animation_with_color("car-right-white", "car-right-blue", color.by_name["blue"])
        self.__blend_animation_with_color("car-up-white", "car-up-blue", color.by_name["blue"])

        self.__blend_animation_with_color("car-left-white", "car-left-green", color.by_name["green"])
        self.__blend_animation_with_color("car-down-white", "car-down-green", color.by_name["green"])
        self.__blend_animation_with_color("car-right-white", "car-right-green", color.by_name["green"])
        self.__blend_animation_with_color("car-up-white", "car-up-green", color.by_name["green"])

        # use __blend_animation_with_color to change color of the
        # sprite. You can use it for very simple skins
        # i.e.
        # __blend_animation_with_color("template-guy", "green-guy", color.by_name["green"])

    def load_font_files(self):
        # add filename without extension here (i.e. 'main' will
        # load 'main.ttf' file)
        # add fonts in format
        # (fontname, fontsize)
        files = [("LESSERCO", 36),
                 ("LESSERCO", 90)]
        for file in files:
            self.load_font_file(file[0], file[1])

    ## use resources
    def sounds_play(self, name, loop=0):
        if self.cfg.sound and name in self.sounds:
            return self.sounds[name].play(loop)

    def music_play(self, name, repeat=-1):
        if self.cfg.music and name in self.music:
            pygame.mixer.music.load(self.music[name])
            pygame.mixer.music.play(repeat)

    def music_stop(self):
        if self.cfg.music:
            pygame.mixer.music.stop()

    def font_render(self, name, size, text, color):
        return self.font[name][size].render(text, 1, color)

    ## load files
    def load_sound_file(self, name):
        sound = self.sounds[name] = pygame.mixer.Sound(self.cfg.sounds_path(name + ".ogg"))
        return sound

    def load_music_file(self, name):
        music = self.music[name] = self.cfg.music_path(name + ".ogg")
        return music

    def load_font_file(self, name, size):
        try:
            self.font[name]
        except:
            self.font[name] = {}
        font = self.font[name][size] = pygame.font.Font(self.cfg.font_path(name + ".ttf"), size)
        return font

    def load_animation_file(self, name):
        if os.path.isfile(self.cfg.gfx_path(name) + ".png"): # there is only one static image
            img = self.__load_image(self.cfg.gfx_path(name) + ".png")
            self.animation[name] = []
            self.animation[name].append(img)
            return self.animation
        else: # there is a sequence of images - an animation
            count = 0
            animation = []
            while True:
                fname = self.cfg.gfx_path(name) + "-" + str(count) + ".png"
                if not os.path.isfile(fname):
                    break
                animation.append(self.__load_image(fname))
                count += 1
            self.animation[name] = animation
            return animation

    def __load_image(self, fname):
        return pygame.image.load(self.cfg.gfx_path(fname)).convert_alpha()

    def __blend_animation_with_color(self, name, new_name, color):
        """ Usefull for theme/skin creation

        You create file with everything in mostly white color, then
        you use this function and you get new animation with changed
        colors to 'color'
        """
        animation = self.animation[name]
        new_animation = []
        for frame in animation:
            new_frame = frame.copy()
            s = pygame.Surface(frame.get_size()).convert_alpha()
            s.fill(color)
            new_frame.blit(s, (0,0), None, BLEND_RGBA_MULT)
            new_animation.append(new_frame)
        self.animation[new_name] = new_animation
        return new_animation

    def __map_animation_frames(self, name, new_name, f):
        """ Apply f to all frames of an animation and store as new animation
        """
        animation = self.animation[name]
        new_animation = []
        for frame in animation:
            new_frame = f(frame)
            new_animation.append(new_frame)
        self.animation[new_name] = new_animation
        return new_animation

    def __rotate_image(self, degrees):
        return lambda image: pygame.transform.rotate(image, degrees)

    def __flip_image(self):
        return lambda image: pygame.transform.flip(image, True, False)
