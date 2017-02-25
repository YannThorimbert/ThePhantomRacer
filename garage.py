import pygame
from pygame.math import Vector3 as V3
import thorpy
import core3d, parameters, camera, light, primitivemeshes
from light import Material

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


def wings_rect(a,b,color,x=0.,y=0.,angle=0.):
    w = primitivemeshes.rectangle(a,b,color)
    w.rotate_around_center_x(-90)
    w.from_init_rot = V3()
    w2 = w.get_copy()
##    w.move(V3(0,-a,0)) #biplan
##    w2.move(V3(0,a,0))
    w.move(V3(x,y,-b/2-1)) #monoplan
    w.rotate_around_center_x(angle)
    w2.move(V3(x,y,b/2+1))
    w2.rotate_around_center_x(-angle)
    w.from_init = V3()
    w2.from_init = V3()
##    w = w.get_splitted_copy()
    return w,w2

def wings_free(a,b,c,d,fleche,color,angle=0.,y=0,sym=True):
    assert d < 0
    p1 = V3()
    p2 = p1 + V3(0,0,a)
    p3 = p2 + V3(b,0,-fleche)
    p4 = p3 + V3(c,0,d)
##    mesh = core3d.Area3D([p1,p2,p3,p4],color)
    t1 = core3d.Triangle(p1,p2,p3)
    t2 = core3d.Triangle(p1,p3,p4)
    mesh = core3d.ManualObject3D([t1,t2])
    mesh.refresh_normals()
    mesh.refresh()
    mesh.rotate_around_center_y(90)
    delta = -1
    if not sym: delta*=-1
    mesh.move(V3(-1,y,delta))
    mesh.from_init = V3()
    mesh.rotate_around_center_x(angle)
    mesh.from_init_rot = V3()
    mesh.set_color(color)
    #
##    p = []
##    for v in [p1,p2,p3,p4]:
##        p.append(v+V3(0,0,2*v.z))
##    t1 = core3d.Triangle(p[0],p[1],p[2])
##    t2 = core3d.Triangle(p[0],p[2],p[3])
##    mesh2 = core3d.ManualObject3D([t1,t2])
##    mesh2.refresh_normals()
##    mesh2.refresh()
##    mesh2.set_color(color)
    if sym:
        return mesh, wings_free(a,-b,-c,d,fleche,color,-angle,y,False)
    else:
        return mesh


class Garage:

    def __init__(self):
        self.screen = thorpy.get_screen()
        #
        light_pos = V3(0,1000,-1000)
        light_m = V3(20,20,20)
        light_M = V3(200,200,200)
        self.light = light.Light(light_pos, light_m, light_M)
        #
        self.e_bckgr = thorpy.Background((255,255,255))
        self.t, self.n, self.c = cut_vessel("a.stl",
                                            Material((0,0,255)),
                                            Material((0,0,0)))
##        self.w = wings_rect(1.5,2.5,self.t.triangles[0].color,
##                            y=0.5,
##                            angle=10.)
        self.w = wings_free(1.3,3.,0.2,-0.5,1.,self.t.triangles[0].color, 10., y=0.)
        self.parts = [self.t, self.n, self.c, self.w[0], self.w[1]]
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
        #
        self.viewport = pygame.Surface((400,400))
        self.viewport_color = (200,200,200)
        self.viewport_rect = pygame.Rect((0,0),self.viewport.get_size())
        self.viewport_rect.right = parameters.W - 20
        self.viewport_rect.centery = parameters.H//2
        self.cam = camera.Camera(self.viewport, fov=512, d=2, objs=[])
        #
        #
        #
        self.e_ok = thorpy.make_button("Done", func=thorpy.functions.quit_menu_func)
        #
        vw,vh = self.viewport_rect.size
        self.e_viewport_frame = thorpy.Element()
        painter = thorpy.painterstyle.ClassicFrame((vw+3,vh+3),
                                                    color=self.viewport_color,
                                                    pressed=True)
        self.e_viewport_frame.set_painter(painter)
        self.e_viewport_frame.finish()
        self.e_viewport_frame.set_center(self.viewport_rect.center)
        #
        self.e_bckgr.add_elements([self.e_ok,self.e_viewport_frame])

    def refresh_parts(self):
        self.parts = [self.t, self.n, self.c, self.w[0], self.w[1]]
        self.triangles = []
        for p in self.parts:
            self.triangles += p.triangles

    def refresh_display(self):
        for p in self.parts:
            p.rotate_around_center_y(1)
        self.viewport.fill(self.viewport_color)
##        self.screen.fill((255,255,255))
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
                    self.cam.draw_object(self.viewport, p, color)
        self.screen.blit(self.viewport,self.viewport_rect)
        pygame.display.update(self.viewport_rect)
##        pygame.display.flip()

    def mousemotion(self,e):
        if pygame.mouse.get_pressed()[0]:
            dcx = e.pos[0] - self.viewport_rect.centerx#parameters.W//2
            dcy = e.pos[1] - self.viewport_rect.centery#parameters.H//2
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