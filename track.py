from pygame.math import Vector3 as V3
import primitivemeshes
from core3d import Path3D, Object3D, ManualObject3D
import parameters

def get_type(thing):
    if isinstance(thing, Object3D) or isinstance(thing, ManualObject3D):
        return "o"
    else:
        return "p"

class ThingManager:

    def __init__(self, n, maxn, spacing):
        self.n = n
        self.maxn = maxn
        self.spacing = spacing
        self.spacing_move = V3(0,0,maxn*spacing)
        self.counter = 0

    def increment(self):
        self.counter += 1

    def get_remaining(self):
        return self.n - self.counter

    def should_continue(self):
        remaining = self.n - self.counter
        return remaining > self.maxn

class Track:

    def __init__(self, x1, x2, y=None):
        self.things_objects = []
        self.things_paths = []
        self.obstacles_objects = []
        self.obstacles_paths = []
        #
        self.y = y
        if self.y is None:
            self.y = parameters.GROUND + 1
        self.x1 = x1
        self.x2 = x2

    def add_thing(self, thing, frompos, topos, spacing, maxn):
        n = (topos-frompos)//spacing
        if maxn is None:
            maxn = n
        manager = ThingManager(n, maxn, spacing)
        type_ = get_type(thing)
        actual_number_drawn = min(n,maxn)
        for i in range(actual_number_drawn):
            cpy = thing.get_copy()
            cpy.move(V3(0,0,frompos+i*spacing))
            cpy.manager = manager
            if type_ == "p":
                self.things_paths.append(cpy)
            else:
                self.things_objects.append(cpy)

    def add_obstacle(self, obstacle):
        type_ = get_type(obstacle)
        if type_ == "p":
            self.obstacles_paths.append(obstacle)
        else:
            self.obstacles_objects.append(obstacle)


    def get_all_objs(self):
        return self.things_objects + self.things_paths +\
                self.obstacles_objects + self.obstacles_paths

    def get_nonthings(self):
        return self.obstacles_objects + self.obstacles_paths

    def refresh_and_draw_things(self, cam, light):
        #things never overlap, and can never appear in front of an object
        for thing in self.things_objects:
            if thing.visible:
                thing.refresh()
                for t in thing.triangles:
                    if t.c.z > 0: #c denotes the center coordinate
                        p = []
                        for v in t.vertices():
                            x,y = cam.project(v)
                            p.append((int(x),int(y)))
                            color = light.get_color(t)
                        cam.draw_object(cam.screen, p, color)
                    elif thing.manager.should_continue():
                        thing.move(thing.manager.spacing_move)
                        thing.manager.increment()
        for thing in self.things_paths:
            if thing.visible:
                p = []
                for t in thing.points:
                    if t.z > 0 and t.y > parameters.GROUND:
                        x,y = cam.project(t)
                        p.append((int(x),int(y)))
                        if thing.closed:
                            if len(p) > 2:
                                if self.filled:
                                    cam.draw_filled_polygon(cam.screen, p, self.color)
                                else:
                                    cam.draw_polygon(cam.screen, p, self.color)
                        else:
                            if len(p) > 1:
                                cam.draw_path(cam.screen, p, thing.color)
                    elif thing.manager.should_continue():
                        thing.move(thing.manager.spacing_move)
                        thing.manager.increment()

