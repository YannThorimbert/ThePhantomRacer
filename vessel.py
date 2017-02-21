from pygame.math import Vector3 as V3
import core3d, parameters


class Move:

    def __init__(self, vel, fighter, type_):
        self.vel = vel
        self.fighter = fighter
        self.dest = None #x coordinate
        self.last_pressed = 0
        if type_ == "h":
            self.refresh = self.refresh_x
        elif type_ == "v":
            self.refresh = self.refresh_y
        else:
            raise Exception("Uknown type",type_)

    def go_to(self, dest, i):
        if i > self.last_pressed + parameters.MOVE_DELTA_I:
            self.dest = dest
            self.last_pressed = i
            return True
        return False

    def refresh(self):
        pass

    def refresh_x(self):
        if self.dest is not None:
            delta = self.dest - parameters.scene.cam.from_init.x
##            print("r        ", delta, self.dest, parameters.scene.cam.from_init.x)
            abs_delta = abs(delta)
            if abs_delta < 0.1:
                self.dest = None
                return 0.
            if abs_delta > self.vel:
                return self.vel * delta/abs_delta
            return delta
        return 0.

    def refresh_y(self):
        if self.dest is not None:
            delta = self.dest - parameters.scene.cam.from_init.y
##            print("r        ", delta, self.dest, parameters.scene.cam.from_init.x)
            abs_delta = abs(delta)
            if abs_delta < 2:
                self.dest = None
                return 0.
            if abs_delta > self.vel:
                return self.vel * delta/abs_delta
            return delta
        return 0.


#nouvelle politique:
#   quand user appuie sur une touche, on entame la transition vers autre rail,
#   jusqu'a ce que l'autre rail soit atteint, sauf si user appuie sur une touche,
#   auquel cas la destination est incrementee
#       ==> attributs: dest, vel
#   Eventuellement: smoothing des derniers steps.

class Dynamics:

    def __init__(self, xvel, yvel, fighter):
        self.h = Move(xvel, fighter, "h")
        self.v = Move(yvel, fighter, "v")
        self.velocity = V3()

    def refresh(self):
        self.velocity.x = self.h.refresh()
        self.velocity.y = self.v.refresh()



class Vessel(core3d.Object3D):

    def __init__(self, filename, more_triangles=None):
        core3d.Object3D.__init__(self,filename, more_triangles)
        self.dynamics = None
        self.railx = None
        self.raily = None

    def handle_obstacle_collision(self, obstacle):
        obstacle.obj.visible = False
##        parameters.scene.track.obstacles.remove(obstacle)

