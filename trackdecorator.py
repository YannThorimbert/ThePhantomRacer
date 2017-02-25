from pygame.math import Vector3 as V3

import primitivemeshes, parameters
from light import Material

class Decorator:

    def __init__(self, track):
        self.track = track
        scene = parameters.scene
        #
        track.add_visual_rails()
        #
        cpies = []
        for i in range(track.ny):
            cpies += self.add_arrows(i, 25*i, track.zfinish)
        #
        squares = self.add_globs_square(0, 500)
        circles = self.add_globs_circle(500, 1000)
        squares2 = self.add_globs_square(1000, track.zfinish)
        #
        self.color_sign = 5
        self.color = 1
        self.material = Material((255,0,0))
        for c in cpies:
            c.set_color(self.material)
        def f():
            self.color += self.color_sign
            if self.color >= 255:
                self.color = 255
                self.color_sign *= -1
            elif self.color <= 0:
                self.color = 0
                self.color_sign *= -1
            for c in cpies:
##                c.set_color(Material(255,self.color,0))
                self.material.col[1] = self.color
                self.material.m[1] = self.color / 0.2
                self.material.M[1] = min(self.color*1.1 + 100,255)
##                c.rotate_around_center_z(1)
##                c.move(V3(0,0,-1))
            for g in circles:
                g.rotate_around_center_z(2)
        track.functions_things = f

    def add_arrows(self, raily, frompos, topos, maxn=10, d=5, spacing=60,
                             bothsides=True):
        y = self.track.rails[0,raily].middlepos.y
        r,t = primitivemeshes.p_arrow(5,20,2,(255,0,0))
        r.move(V3(-d,y,0))
        t.move(V3(-d,y,0))
        r.rotate_around_center_z(90)
        t.rotate_around_center_z(90)
        r.rotate_around_center_y(90)
        t.rotate_around_center_y(90)
        #
        cpies = []
        cpies += self.track.add_thing(r,frompos,topos,50,maxn)
        cpies += self.track.add_thing(t,frompos,topos,50,maxn)
        if bothsides:
            r2,t2 = r.get_copy(), t.get_copy()
            r2.move(V3(2*d+parameters.RAILW*self.track.nx,0,0))
            t2.move(V3(2*d+parameters.RAILW*self.track.nx,0,0))
            cpies += self.track.add_thing(r2,frompos,topos,spacing,maxn)
            cpies += self.track.add_thing(t2,frompos,topos,spacing,maxn)
        return cpies

    def add_globs_square(self, frompos, topos, spacing=60, maxn=10):
        glob = primitivemeshes.p_rectangle(self.track.nx*parameters.RAILW,
                                            self.track.ny*parameters.RAILH,
                                            filled=False)
        glob.move(V3(self.track.nx*parameters.RAILW//2,
                    self.track.ny*parameters.RAILH//2,0))
        glob.closed = False
        globs = self.track.add_thing(glob, frompos, topos, spacing, maxn)
        return globs

    def add_globs_circle(self, frompos, topos, n=10, spacing=60, maxn=10):
        radius = max(self.track.nx*parameters.RAILW,
                        self.track.ny*parameters.RAILH)
        radius *= 1.5
        glob = primitivemeshes.p_disk(radius/2, False, n=n)
        glob.move(V3(self.track.nx*parameters.RAILW//2,
                    self.track.ny*parameters.RAILH//2,0))
        glob.closed = False
        globs = self.track.add_thing(glob, frompos, topos, spacing, maxn)
        return globs