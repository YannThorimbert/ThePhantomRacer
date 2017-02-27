import random
import pygame
from pygame.math import Vector3 as V3
import thorpy
import core3d, parameters, camera, light, primitivemeshes
from light import Material



def color_glasses(model, glass_color):
    tail, nose, cock = [], [], []
    for t in model.original_triangles:
        x = [p.x for p in t.vertices()]
        if max(x) <= -2.:
            tail.append(t)
        elif min(x) >= 2.:
            nose.append(t)
        else:
            cock.append(t)
##    tail = core3d.ManualObject3D(tail)
##    nose = core3d.ManualObject3D(nose)
##    cock = core3d.ManualObject3D(cock)
    for t in cock:
        if sum([abs(value)>1e-6 for value in t.compute_normal()]) > 1:
            t.color = glass_color


def cut_object(filename, color, glass_color):
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
   return [tail, nose, cock]


def generate_vessel(color, glass_color):
    t = random.choice(parameters.MODELS)+".stl"
    n = random.choice(parameters.MODELS)+".stl"
    c = random.choice(parameters.MODELS)+".stl"
    #
    t =  cut_object(t,color,glass_color)[0]
    n =  cut_object(n,color,glass_color)[1]
    c =  cut_object(c,color,glass_color)[2]
    return core3d.ManualObject3D(t.triangles+n.triangles+c.triangles)



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
    if sym:
        t1 = core3d.Triangle(p1,p2,p3)
        t2 = core3d.Triangle(p1,p3,p4)
    else:
        t1 = core3d.Triangle(p3,p2,p1)
        t2 = core3d.Triangle(p4,p3,p1)
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
    if sym:
        return mesh, wings_free(a,-b,-c,d,fleche,color,-angle,y,False)
    else:
        return mesh

##import vessel
# def build_all_parts():
#    parameters.canonic_vessels = {}
#    color = Material((200,200,200))
#    glass = Material((0,0,0))
#    files = ["Aerocrush","BangDynamics"]
#    for f in files:
#        parts = wings_free(1.3,3.,0.2,-0.5,1.,color,10.,y=0.)
#        triangles = []
#        for p in parts:
#            triangles += p.triangles
#        parameters.canonic_vessels[f] = vessel.Vessel(f+".stl",triangles)


def launch_rankings():
    elements = []
    import gamelogic
    gamelogic.refresh_ranking()
    for i,p in enumerate(parameters.players):
        if i == 0:
            elements.append(thorpy.make_text("-----Intergalactic category-----",font_color=(0,155,0)))
        elif i == parameters.NPLAYERS//3:
            elements.append(thorpy.make_text("-----International category-----",font_color=(0,155,0)))
        elif i == 2*parameters.NPLAYERS//3:
            elements.append(thorpy.make_text("-----National category-----",font_color=(0,155,0)))
        if p == parameters.player:
            elements.append(thorpy.make_text("("+str(p.points)+")  "+p.name,font_color=(255,0,0)))
        else:
            elements.append(thorpy.make_text("("+str(p.points)+")  "+p.name))

    box = thorpy.Box.make(elements,size=(300,300))
    box.refresh_lift()
    box2 = thorpy.make_ok_box([box])
##    box.set_size((300,300))
##    box.refresh_lift()
    thorpy.launch(box2)

def quit_game():
    thorpy.functions.quit_func()


class Garage:

    def __init__(self):
##        if not parameters.canonic_vessels:
##            get_all_parts()
        self.vessel = parameters.player.vessel.get_copy()
        self.ovessel = parameters.player.vessel
        self.screen = thorpy.get_screen()
        #
        light_pos = V3(0,1000,-1000)
        light_m = V3(20,20,20)
        light_M = V3(200,200,200)
        self.light = light.Light(light_pos, light_m, light_M)
        #
        self.e_bckgr = thorpy.Background.make((255,255,255))
        self.vessel.set_pos(parameters.GARAGE_POS)
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
        self.e_ok = thorpy.make_button("Go to next race", func=thorpy.functions.quit_menu_func)
        self.e_ok.set_main_color((0,255,0))
        self.e_ok.set_font_size(thorpy.style.FONT_SIZE+3)
        self.e_ok.scale_to_title()
        #
        def choice_repair():
            cost = (self.ovessel.max_life - self.ovessel.life)*300
            if cost <= parameters.player.money:
                if thorpy.launch_binary_choice("Are you sure? This will cost "+\
                                                str(cost)+"$"):
                    self.ovessel.life = self.ovessel.max_life
                    parameters.player.money -= cost
                    damages = str(round(100.*(1. - self.ovessel.life/self.ovessel.max_life)))
                    self.e_damage.set_text("Vessel damages: " + damages + "%")
                    self.e_money.set_text("Money: "+str(parameters.player.money)+" $")
            else:
                thorpy.launch_blocking_alert("Repairing costs "+str(cost)+" $. You don't have enough money.")
            self.e_bckgr.blit()
            self.refresh_display()
            pygame.display.flip()
        self.e_repair = thorpy.make_button("Repair vessel",choice_repair)
        #
        damages = str(round(100.*(1. - self.ovessel.life/self.ovessel.max_life)))
        self.e_damage = thorpy.make_text("Vessel damages: " + damages + "%")
        self.e_ranking = thorpy.make_button("See rankings", launch_rankings)
        self.e_menu = thorpy.make_button("Stop career and die (forever)",
                                        func=quit_game)
        self.e_menu.set_main_color((255,0,0))
        self.e_menu.set_font_size(thorpy.style.FONT_SIZE-2)
        self.e_menu.scale_to_title()
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
        import hud
        fuel = str(round(100*self.ovessel.engine.fuel/self.ovessel.engine.max_fuel))
        self.e_fuel = hud.LifeBar("Fuel: "+fuel+" %",text_color=(255,0,0),size=(100,30))
        self.e_fuel.set_life(self.ovessel.engine.fuel/self.ovessel.engine.max_fuel)
        def choice_refuel():
            cost = (self.ovessel.engine.max_fuel - self.ovessel.engine.fuel)//2
            if cost <= parameters.player.money:
                if thorpy.launch_binary_choice("Are you sure? This will cost "+\
                                                str(cost)+"$"):
                    self.e_fuel.set_life(1.)
                    self.e_fuel.set_life_text("Fuel: 100 %")
                    parameters.player.money -= cost
                    self.e_money.set_text("Money: "+str(parameters.player.money)+" $")
                    self.ovessel.engine.fuel = self.ovessel.engine.max_fuel
            else:
                thorpy.launch_blocking_alert("Refueling costs "+str(cost)+" $. You don't have enough money.")
            self.e_bckgr.blit()
            self.refresh_display()
            pygame.display.flip()
        self.e_refuel = thorpy.make_button("Refuel",choice_refuel)
        self.e_money = thorpy.make_text("Money: "+str(parameters.player.money)+" $",
                                        thorpy.style.TITLE_FONT_SIZE,(255,0,0))
        self.e_money.stick_to("screen","top","top")
        self.e_money.move((0,30))
        #
        self.e_box = thorpy.Box.make([self.e_damage,self.e_repair,
                                    thorpy.Line.make(100,"h"),self.e_fuel,
                                    self.e_refuel,
                                    thorpy.Line.make(100,"h"),
                                    self.e_ranking,self.e_ok])
        self.e_bckgr.add_elements([self.e_box,self.e_menu])
        thorpy.store(self.e_bckgr, x = 200)
        self.e_bckgr.add_elements([self.e_viewport_frame,self.e_money])
        self.e_menu.move((0,30))

    def refresh_display(self):
        self.vessel.rotate_around_center_y(1)
        self.viewport.fill(self.viewport_color)
        self.vessel.refresh_and_draw(self.cam, self.light)
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
            self.vessel.rotate_around_center_x(rotate_x)
            self.vessel.rotate_around_center_y(rotate_y)
            self.vessel.rotate_around_center_z(rotate_z)
##            self.refresh_parts()

    def play(self):
        m = thorpy.Menu(self.e_bckgr)
        m.play()




##class Garage:
##
##    def __init__(self):
####        if not parameters.canonic_vessels:
####            get_all_parts()
##        self.vessel = parameters.player.vessel
##        self.screen = thorpy.get_screen()
##        #
##        light_pos = V3(0,1000,-1000)
##        light_m = V3(20,20,20)
##        light_M = V3(200,200,200)
##        self.light = light.Light(light_pos, light_m, light_M)
##        #
##        self.e_bckgr = thorpy.Background.make((255,255,255))
##        self.t, self.n, self.c = cut_object("BangDynamics.stl",
##                                            Material((0,0,255)),
##                                            Material((0,0,0)))
##        self.w = wings_rect(1.5,2.5,self.t.triangles[0].color,
##                            y=0.5,
##                            angle=10.)
##        self.w = wings_free(1.3,3.,0.2,-0.5,1.,self.t.triangles[0].color, 10., y=0.)
##        self.parts = [self.t, self.n, self.c, self.w[0], self.w[1]]
##        self.triangles = []
##        for p in self.parts:
##            self.triangles += p.triangles
##        for p in self.parts:
##            p.move(parameters.GARAGE_POS)
##        reaction =  thorpy.ConstantReaction(thorpy.THORPY_EVENT,
##                                            self.refresh_display,
##                                            {"id":thorpy.constants.EVENT_TIME})
##        self.e_bckgr.add_reaction(reaction)
##        reaction = thorpy.Reaction(pygame.MOUSEMOTION, self.mousemotion)
##        self.e_bckgr.add_reaction(reaction)
##        #
##        self.viewport = pygame.Surface((400,400))
##        self.viewport_color = (200,200,200)
##        self.viewport_rect = pygame.Rect((0,0),self.viewport.get_size())
##        self.viewport_rect.right = parameters.W - 20
##        self.viewport_rect.centery = parameters.H//2
##        self.cam = camera.Camera(self.viewport, fov=512, d=2, objs=[])
##        #
##        #
##        #
##        self.e_ok = thorpy.make_button("Done", func=thorpy.functions.quit_menu_func)
##        #
####        names = [thorpy.make_button(name) for name in parameters.player.parts]
####        self.e_names = thorpy.Box.make(names)
####        self.e_names.stick_to(self.viewport_rect,"left","right")
####        self.e_sell = thorpy.make_button("Sell vessel")
####        self.e_buy = thorpy.make_button("Buy vessel")
##        def choice_repair():
##            cost = self.vessel.max_life - self.vessel.life
##            if cost <= parameters.player.money:
##                if thorpy.launch_binary_choice("Are you sure? This will cost "+\
##                                                str(cost)+"$"):
##                    print("repair")
##                else:
##                    print("don't repair")
##            else:
##                thorpy.launch_alert("Repairing costs "+str(cost)+"$. You don't have enough money.")
##            self.e_bckgr.blit()
##            self.refresh_display()
##            pygame.display.flip()
##        self.e_repair = thorpy.make_button("Repair vessel",choice_repair)
##        #
##        vw,vh = self.viewport_rect.size
##        self.e_viewport_frame = thorpy.Element()
##        painter = thorpy.painterstyle.ClassicFrame((vw+3,vh+3),
##                                                    color=self.viewport_color,
##                                                    pressed=True)
##        self.e_viewport_frame.set_painter(painter)
##        self.e_viewport_frame.finish()
##        self.e_viewport_frame.set_center(self.viewport_rect.center)
##        #
##        self.e_bckgr.add_elements([self.e_ok,self.e_repair,self.e_viewport_frame])
##        thorpy.store(self.e_bckgr, [self.e_ok,self.e_repair], x = 100)
##
##
##    def refresh_parts(self):
##        self.parts = [self.t, self.n, self.c, self.w[0], self.w[1]]
##        self.triangles = []
##        for p in self.parts:
##            self.triangles += p.triangles
##
##    def refresh_display(self):
##        for p in self.parts:
##            p.rotate_around_center_y(1)
##        self.viewport.fill(self.viewport_color)
####        self.screen.fill((255,255,255))
####            p.refresh_and_draw(self.cam, self.light)
##        for t in self.triangles:
##            t.refresh_cd()
##        for t in self.triangles:
##            t.refresh_pd()
##        self.triangles.sort(key=lambda x:x.pd, reverse=True)
##        for t in self.triangles:
##            if t.c.z > 1 and t.c.z < parameters.VISIBILITY: #c denotes the center coordinate
##                p = []
##                for v in t.vertices():
##                    x,y = self.cam.project(v)
##                    if abs(x) < parameters.W and abs(y) < parameters.H:
##                        p.append((int(x),int(y)))
##                    else:
##                        break
##                if len(p) == 3:
##                    color = self.light.get_color(t)
##                    self.cam.draw_object(self.viewport, p, color)
##        self.screen.blit(self.viewport,self.viewport_rect)
##        pygame.display.update(self.viewport_rect)
####        pygame.display.flip()
##
##    def mousemotion(self,e):
##        if pygame.mouse.get_pressed()[0]:
##            dcx = e.pos[0] - self.viewport_rect.centerx#parameters.W//2
##            dcy = e.pos[1] - self.viewport_rect.centery#parameters.H//2
##            dist = dcx*dcx + dcy*dcy
##            k = -1.
##            #a*rotate_z + (1-a)*rotate_x = k*rel.y
##            #rotate_y = k*rel.x
##            #dist grand : a grand
##            a = dist / float(parameters.W//2)**2
##            rotate_z = a * k * e.rel[1]
##            rotate_x = (1.-a) * k * e.rel[1]
##            rotate_y = k * e.rel[0]
##            for p in self.parts:
##                p.rotate_around_center_x(rotate_x)
##                p.rotate_around_center_y(rotate_y)
##                p.rotate_around_center_z(rotate_z)
##            self.refresh_parts()
##
##    def play(self):
##        m = thorpy.Menu(self.e_bckgr)
##        m.play()
