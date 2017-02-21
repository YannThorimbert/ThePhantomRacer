from pygame.math import Vector3 as V3

W,H = 900,600
FPS = 40

MOVE_DELTA_I = 5
VISIBILITY = 500#not used
N_DESTROY = 20
SPEED = 0#to be deleted
HERO_POS = V3(0,-4,15)

MIN_BOX_THICKNESS = 10

RAILW = 12
RAILH = 12

TURN = 1. / 10.
FRICTION = 1. / 500.


scene = None

