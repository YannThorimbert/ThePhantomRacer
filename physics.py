from pygame.math import Vector3 as V3

class Physics:

    def __init__(self):
        self.pos = V3()
        self.vel = V3()
        self.rot = V3() #vitesse de rotation