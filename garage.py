import pygame
from pygame.math import Vector3 as V3
import thorpy
import core3d, parameters, camera, light
from light import Material

END_NOSE = -1
END_COCKPIT = 1

def cut_vessel(filename, color, glass_color):
    model = core3d.Object3D(filename)
    model.set_color(color)
    model.rotate_around_center_x(-90)
    model.from_init_rot = V3()
    tail, nose, cock = [], [], []
    for t in model.triangles:
        x = [p.x for p in t.vertices()]
        if max(x) <= -2.:
            tail.append(t)
        elif min(x) >= 2.:
            nose.append(t)
        else:
            cock.append(t)
    tail = core3d.ManualObject3D(tail)
    nose = core3d.ManualObject3D(nose)
    cock = core3d.ManualObject3D(cock)
    for t in cock.triangles:
        if sum([abs(value)>1e-6 for value in t.compute_normal()]) > 1:
            t.color = glass_color
    return tail, nose, cock

##a,b,c = cut_vessel("a.stl")



class Garage:

    def __init__(self):
        self.screen = thorpy.get_screen()
        #
        self.cam = camera.Camera(self.screen, fov=512, d=2, objs=[])
        light_pos = V3(0,1000,-1000)
        light_m = V3(20,20,20)
        light_M = V3(200,200,200)
        self.light = light.Light(light_pos, light_m, light_M)
        #
        self.e_bckgr = thorpy.Background((255,255,255))
        self.t, self.n, self.c = cut_vessel("a.stl",
                                            Material((0,0,255)),
                                            Material((0,0,0)))
        self.parts = [self.t, self.n, self.c]
        self.triangles = []
        for p in self.parts:
            self.triangles += p.triangles
        for p in self.parts:
            p.move(parameters.GARAGE_POS)
        reaction =  thorpy.ConstantReaction(thorpy.THORPY_EVENT,
                                            self.refresh_display,
                                            {"id":thorpy.constants.EVENT_TIME})
        self.e_bckgr.add_reaction(reaction)
        reaction = thorpy.Reaction(pygame.MOUSEMOTION, self.mousemotion)
        self.e_bckgr.add_reaction(reaction)

    def refresh_parts(self):
        self.parts = [self.t, self.n, self.c]
        self.triangles = []
        for p in self.parts:
            self.triangles += p.triangles

    def refresh_display(self):
        self.screen.fill((255,255,255))
##            p.refresh_and_draw(self.cam, self.light)
        for t in self.triangles:
            t.refresh_cd()
        for t in self.triangles:
            t.refresh_pd()
        self.triangles.sort(key=lambda x:x.pd, reverse=True)
        for t in self.triangles:
            if t.c.z > 1 and t.c.z < parameters.VISIBILITY: #c denotes the center coordinate
                p = []
                for v in t.vertices():
                    x,y = self.cam.project(v)
                    if abs(x) < parameters.W and abs(y) < parameters.H:
                        p.append((int(x),int(y)))
                    else:
                        break
                if len(p) == 3:
                    color = self.light.get_color(t)
                    self.cam.draw_object(self.screen, p, color)
        pygame.display.flip()

    def mousemotion(self,e):
        if pygame.mouse.get_pressed()[0]:
            dcx = e.pos[0] - parameters.W//2
            dcy = e.pos[1] - parameters.H//2
            dist = dcx*dcx + dcy*dcy
            k = -1.
            #a*rotate_z + (1-a)*rotate_x = k*rel.y
            #rotate_y = k*rel.x
            #dist grand : a grand
            a = dist / float(parameters.W//2)**2
            rotate_z = a * k * e.rel[1]
            rotate_x = (1.-a) * k * e.rel[1]
            rotate_y = k * e.rel[0]
            for p in self.parts:
                p.rotate_around_center_x(rotate_x)
                p.rotate_around_center_y(rotate_y)
                p.rotate_around_center_z(rotate_z)
            self.refresh_parts()

    def play(self):
        m = thorpy.Menu(self.e_bckgr)
        m.play()