DIR_LEFT                      = 0
DIR_DOWN                      = 1
DIR_RIGHT                     = 2
DIR_UP                        = 3
DIR_STOP                      = 4

ORIGIN_TOP_LEFT               = 4
ORIGIN_CENTER                 = 5

LEFT = (-1, 0)
RIGHT = (1, 0)
UP = (0, -1)
DOWN = (0, 1)

opposite = {LEFT:set([UP, DOWN]), RIGHT:set([UP, DOWN]), UP:set([LEFT, RIGHT]), DOWN:set([LEFT, RIGHT])}

WIDTH = 800
HEIGHT = 600
