from pygame.math import Vector3 as V3

##class Move:
##
##    def __init__(self, obj, axis, d, t, a):
##        self.displacement = V3()
##        self.displacement[axis] = d
##        if axis == 0: #displacement x <--> rotate z
##            self.func = obj.rotate_around_center_z
##        elif axis == 1: #displacement y <--> rotate x
##            self.func = obj.rotate_around_center_x
##        else:
##            raise Exception("Move only for x or y displacement")
##        self.time = t #semi time actually
##        self.time2 = 2*self.time
##        self.amount = a
##        #
##        self.delta_angle = self.amount / self.time
##        self.i = -1
##
##    def start(self): #set angle!
##        self.i = 0
##
##    def stop(self):
##        self.i = -1 #set angle!
##
##    def refresh(self, cam):
##        if self.i < 0: #nothing to do
##            return
##        else:
##            if self.i < self.time:
##                self.func(self.delta_angle)
##            elif self.i < self.time2:
##                self.func(-self.delta_angle)
##            else:
##                self.i = -1
##                return
##            cam.move(self.displacement)
##            self.i += 1

##class Dynamics: #Does not include acceleration along z !! (todo separately)
##
##    def __init__(self, obj, cam):
##        self.left = Move(obj, 0, -10, 10, 30.)
##        self.right = Move(obj, 0, 1, 10, 30.)
##        self.up = Move(obj, 1, -1, 10, 10.)
##        self.down = Move(obj, 1, 1, 10, 10.)
##        #
##        self.obj = obj
##        self.cam = cam
##
##    def refresh(self):
##        self.left.refresh(self.cam)
##        self.right.refresh(self.cam)
##        self.up.refresh(self.cam)
##        self.down.refresh(self.cam)

class Move:

    def __init__(self, amount, attenuation):
        self.original_amount = amount
        self.a = None
        self.k = attenuation
        self.i = 0

    def restart(self, sign):
        self.a = sign * self.original_amount
        self.i = 1

    def stop(self):
        self.i = 0

    def refresh(self): #linear
        if self.i > 0:
            minus = self.i*self.k*self.a
            if abs(minus) <= abs(self.a): #au lieu de ca on peut precalculer le i auquel ca arrive
                self.i += 1
                return self.a - minus
            else:
                self.stop()
        return 0.

##    def refresh(self): #exponential
##        if self.i > 0:
##            self.a *= self.k
##            print("b", self.a)
##            if abs(self.a) < 0.1:
##                self.stop()
##            else:
##                return self.a
##        return 0.


class Dynamics:

    def __init__(self, ha, hk, va, vk):
        self.h = Move(ha, hk) #linear
        self.v = Move(va, vk)
##        self.h = Move(6., 0.6) #exponential
##        self.v = Move(6., 0.6)
        #
        self.velocity = V3()

    def refresh(self):
        self.velocity.x = self.h.refresh()
        self.velocity.y = self.v.refresh()


