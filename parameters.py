from pygame.math import Vector3 as V3

W,H = 900,600
FPS = 40

AA = True


MODELS = ["Aerocrush","BangDynamics","CabalysticsAndCo","Dropplet","Elbus",
            "F12","GorschType","Herschel","Illuminus"]
HERO_COLOR = (0,0,255)
HERO_MODEL = None
HERO_NAME = "Hero"

MOVE_DELTA_I = 5
VISIBILITY = 800
SPEED = 0#to be deleted
HERO_POS = V3(0,-4,15)

MIN_BOX_THICKNESS = 10

RAILW = 12
RAILH = 12

TURN = 2. / 10.
FRICTION = 1. / 500.
MASS = 1. / 10.

OVERTAKE_SLOWER = 0.75
LIFE_FACTOR = 10
SPEED_HUD = 80.

DEBRIS_SIZE = [0.5, 1.]
N_DEBRIS = 50
DEBRIS_ITER = 100

ANGLE_TURN = 1
ANGLE_TURN_V = 1

VISURAIL_LENGTH = 20
VISURAIL_SPACE = 2*VISURAIL_LENGTH
VISURAIL_NMAX = 10

COLOR_ROTATING = (0,255,0)
COLOR_MOVING = (255,0,0)

GARAGE_POS = V3(0,0,20)

scene = None
player = None
players = []
NPLAYERS = 12
CATEGORIES = ["Intergalatic League", "International Championship", "National cup"]

ZFINISH = 3000
ENGINE_POWER = 0.03

QUIT_GAME = False

ghost = None

def flush():
    global player, scene, players
    for p in players:
        if p.vessel:
            p.vessel.reset()
    scene = None
