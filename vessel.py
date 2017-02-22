import math
from pygame.math import Vector3 as V3
import core3d, parameters


class Move:

    def __init__(self, fighter, type_):
        self.vel = fighter.turn
        self.dest = None #x coordinate
        self.last_pressed = 0
        if type_ == "h":
            self.refresh = self.refresh_x
        elif type_ == "v":
            self.refresh = self.refresh_y
        else:
            raise Exception("Uknown type",type_)

    def reset_i(self):
        self.i = self.last_pressed + parameters.MOVE_DELTA_I + 1

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

    def __init__(self, fighter):
        self.h = Move(fighter, "h")
        self.v = Move(fighter, "v")
        self.velocity = V3()
        self.friction = fighter.friction

    def refresh(self):
        self.velocity.x = self.h.refresh()
        self.velocity.y = self.v.refresh()
        self.velocity.z -= self.friction*self.velocity.z

    def reset_i(self):
        self.h.reset_i()
        self.v.reset_i()


class Part:

    def __init__(self, filename):
##        self.obj = core3d.Object3D(filename)
        self.turn = 1.
        self.friction = 1.
        self.mass = 1.

class Engine(Part):

    def __init__(self, filename):
        Part.__init__(self, filename)
        self.fuel = 10000
        self.force = 0.01

def sign(x):
    if x < 0:
        return -1
    elif x > 0:
        return 1
    return 0

def invsign(x):
    if x < 0:
        return 1
    elif x > 0:
        return -1
    return 0

def collision(v1,v2):
    if v1.mass > v2.mass:
        lightest = v2
        heaviest = v1
    else:
        lightest = v1
        heaviest = v2
    #
    vel = lightest.dyn.velocity
    can = lightest.change_rail(invsign(vel.x),invsign(vel.y))
    if not can:
        vel = heaviest.dyn.velocity
        can = heaviest.change_rail(invsign(vel.x),invsign(vel.y))
        if not can:
            #NB : plutot faire un echange de vitesse du plus grand au + petit!
            if vel.z > lightest.dyn.velocity.z: #lightest is overtaken
                tmp = vel.z
                vel.z = lightest.dyn.velocity.z
                lightest.dyn.velocity.z = tmp
            else: #lightest is overtaking
                lightest.dyn.velocity.z = vel.z*parameters.OVERTAKE_SLOWER
        else:
            heaviest.colliding_with = lightest
    else:
        lightest.colliding_with = heaviest#NB: to reset



class Vessel(core3d.Object3D):
    current_id = 0

    def __init__(self, filename, more_triangles=None):
        core3d.Object3D.__init__(self,filename, more_triangles)
        self.dyn = None
        self.railx = None
        self.raily = None
        self.is_hero = False
        self.colliding_with = None
        #
        self.turn = None
        self.friction = None
        self.mass = None
        self.engine_force = None
        #
        self.nose = Part("")
        self.cockpit = Part("")
        self.tail = Part("")
        self.wings = Part("")
        self.engine = Engine("")
        self.parts = []
        #
        self.name = "no name"
        #
        self.id = Vessel.current_id
        Vessel.current_id += 1

    def change_rail(self, deltax, deltay):
        if deltax:
            track = parameters.scene.track
            newx = self.railx + deltax
            if -1 < newx < track.nx:
                pos = track.rails[newx,self.raily].middlepos.x
                if self.dyn.h.go_to(pos, parameters.scene.i):
                    self.railx += deltax
                    return True
        if deltay:
            track = parameters.scene.track
            newy = self.raily + deltay
            if -1 < newy < track.ny:
                pos = track.rails[self.railx,newy].middlepos.y
                if self.dyn.v.go_to(pos, parameters.scene.i):
                    self.raily += deltay
                    return True
        return False

    def should_collide(self, other):
        if other.id > self.id: #check self != other and forbids double-side collision
            if self.colliding_with is not other: #check that this collision not already currently treated
                if self.box.collide(other.box): #finally check the collision
                    return True
                elif other.box.collide(self.box):
                    return True
        return False


    def obstacle_collision(self, obstacle):
        obstacle.obj.visible = False
        obstacle.living = False
##        parameters.scene.track.obstacles.remove(obstacle)

    def vessel_collision(self, vessel):
        if self.dyn.velocity.x != 0:
            self.dyn.velocity.x *= -10
        elif self.dyn.velocity.y != 0:
            self.dyn.velocity.y *= -1
        elif self.dyn.velocity.z > vessel.dyn.velocity.z:
            if vessel.is_hero:
                self.move(V3(0,0,-20))
            else:
                vessel.move(V3(0,0,20))
        else:
            if vessel.is_hero:
                self.move(V3(0,0,-20))
            else:
                vessel.move(V3(0,0,20))
        #cam move et enlever l'assymetrie?

    def compute_dynamics(self):
        self.parts = [self.nose, self.cockpit, self.tail, self.wings, self.engine]
        self.turn = sum([p.turn for p in self.parts]) * parameters.TURN
        self.friction = sum([p.friction for p in self.parts]) * parameters.FRICTION
        self.mass = sum([p.mass for p in self.parts]) * parameters.MASS
        print("Dynamics:",self.turn,self.friction,self.mass)
        self.dyn = Dynamics(self)
        self.engine_force = self.engine.force/self.mass

    def boost(self):
        if self.engine.fuel > 0:
            self.engine.fuel -= 1
            self.dyn.velocity.z += self.engine_force
        else:
            print("no fuel")
            return 0.