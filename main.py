from pygame.math import Vector3 as V3
import pygame

import thorpy
##from stlreader import Object3D #core3d vs stlreader ==> core un CHOUILLA mieux
from core3d import Object3D, Path3D
from light import Light
from camera import Camera
import primitivemeshes
import parameters
import drawing
import vessel
import random
from scene import Scene
from race import Race
import levelgen

#si autres bugs d'affichages : if len(p) == len(thing.points): dans draw...

#be careful:
#   cam need to know all!!!! (for moving objects)

#faire un grep '#' pour checker qu'il y a pas de trucs importants qqpart

##OverflowError: signed short integer is greater than maximum
#       ==> si continue, faire comme pour Object3D avec control des val abs

#voir si refresh() de object 3d ferait pas mieux d'utiliser version GRU (cf refresh)

2.
#obstacles rotants et mouvants

3.
#meilleur deco

5.
#meilleure levelgen

7.
#garage
##  auto detect parts a partir de mesh entier !!! (coord z th la meme pour debut/fin des parties)


11.
#mode collision ==> explosions (deja fait :) ) (==> parachute si le temps)


# ##############################################################################
#parts:
    #wings
    #derive (traduction?)
    #nose
    #engine (tail)
    #cockpit
#tester la forme la moins bugesque entre section ~cubique et ~triangle
# ##############################################################################

#multilights ?

#deco sur les bords sont des sources de lumiÃ¨re?. En tout cas possedent des couleurs. Clignotent.

#trier les things 1 fois!!!!

#opti: utiliser les dist au carre. Pygame vs math vs manuel

#opti: chaque objet a un facteur k et blit que de 0 a k

#nb opponents: 0, 1, 3 ? ==> varie

#get_copy doit aussi copier frominitrot!!

#things : ronds/carrees englobants. carres parterre

#si temps: ralentisseurs/accele avec fleches clignotantes vertes ou rouges

def init_scene(scene): #debugging only
    parameters.scene = scene
    random.seed(1)
    parameters.scene = scene
    scene.cam = Camera(scene.screen, fov=512, d=2, objs=[])
    scene.cam.set_aa(True)
    #

    light_pos = V3(0,1000,-1000)
    light_m = V3(20,20,20)
    light_M = V3(200,200,200)
    light = Light(light_pos, light_m, light_M)
    scene.light = light
    #hero
    hero_color = V3(70,70,255)
    def wings(a,b,color):
        return primitivemeshes.rectangle(a,b,color).triangles
    def create_vessel(color):
        v = vessel.Vessel("f5.stl",more_triangles=wings(5,1,color))
        v.rotate_around_center_x(-90)
        v.compute_box3D()
        v.set_color(color)
        v.compute_dynamics()
        v.from_init_rot = V3()
        return v
    hero = create_vessel(hero_color)
    hero.is_hero = True
    hero.engine.force *= 1.5
    hero.compute_dynamics()
    hero.mass /= 2.
    hero.name = "Hero"
    ##hero = hero.get_splitted_copy(threshold=-2.5)
    scene.hero = hero
    scene.objs.append(hero)
    #track
    lg = levelgen.LevelGenerator(3000,3,2)
    rw,rh = parameters.RAILW,parameters.RAILH
    possible_obstacles = [primitivemeshes.p_rectangle(0.8*rw,0.8*rh,(0,0,255),(0,0,0))]
##    possible_obstacles = [primitivemeshes.a_rectangle(0.8*rw,0.8*rh,(0,255,255),(0,0,0))]
##    possible_obstacles = [primitivemeshes.rectangle(0.8*rw,0.8*rh,(0,255,255))]
##    possible_obstacles = [primitivemeshes.rectangle(0.8*rw,0.8*rh,(0,255,255)),
##                            primitivemeshes.cube(0.8*rw/2.,(255,0,0))]
    lg.add_static_obstacles(1,possible_obstacles)
    track = scene.track
##    #
##    track.add_visual_rails()
##    #
##    r,t = primitivemeshes.p_arrow(5,20,2,(255,0,0))
##    d = 5
##    maxn = 10
##    r.move(V3(-d,0,0))
##    t.move(V3(-d,0,0))
##    r.rotate_around_center_z(90)
##    t.rotate_around_center_z(90)
##    r.rotate_around_center_y(90)
##    t.rotate_around_center_y(90)
##    cpies = []
##    cpies += track.add_thing(r,0,1000,50,maxn)
##    cpies += track.add_thing(t,0,1000,50,maxn)
##    r2,t2 = r.get_copy(), t.get_copy()
##    r2.move(V3(2*d+parameters.RAILW*track.nx,0,0))
##    t2.move(V3(2*d+parameters.RAILW*track.nx,0,0))
##    cpies += track.add_thing(r2,0,1000,50,maxn)
##    cpies += track.add_thing(t2,0,1000,50,maxn)
##    def f():
##        g = 4*scene.i%255
##        r = 255
##        for c in cpies:
##            c.set_color(V3(r,g,0))
####        if scene.i%10 == 0:
####            if cpies[0].color[0] != 0:
####                for c in cpies:
####                    c.set_color(V3(0,0,255))
####            else:
####                for c in cpies:
####                    c.set_color(V3(255,0,0))
##    track.functions_things = f
    #
    glob = primitivemeshes.p_rectangle(100,100,filled=False)
    glob.move(V3(track.nx*parameters.RAILW,track.ny*parameters.RAILH,0))
    glob.closed = False
    track.add_thing(glob, 0, 1000, 50, maxn=10)
    print("points",glob.points)
    #
    finish = primitivemeshes.rectangle(track.railw,track.railh,(0,255,0))
    for pos in track.rail_centers():
        pos.z = track.zfinish
        finish.set_pos(pos)
        finish.set_color(random.choice(drawing.colors))
        scene.objs.append(finish.get_copy())
    scene.track = track
    scene.opponents = [create_vessel(random.choice(drawing.colors)) for i in range(2)]
    scene.objs += scene.opponents
    #
    scene.refresh_cam()
##    scene.init_cam()
    for i,o in enumerate(scene.opponents):
        scene.put_opponent_on_rail(o,i+1,0,25)
        o.set_ia(100, 0.01)
    hero.set_pos(parameters.HERO_POS)
    scene.put_hero_on_rail(0,0)
    print("end main")
    scene.refresh_vessels()
    hero.set_ia(100, 0.01)
    scene.hud.refresh_attributes()


if __name__ == "__main__":
    app = thorpy.Application((parameters.W,parameters.H))
    screen = thorpy.get_screen()
    ##cam.move(V3(0,20,0))
    g = thorpy.Ghost.make()

##    thorpy.application.SHOW_FPS = True
    race = Race()
    scene = Scene(race)
    race.init_scene(scene)
    reac = thorpy.ConstantReaction(thorpy.THORPY_EVENT,scene.func_time,
                                    {"id":thorpy.constants.EVENT_TIME})
    g.add_reaction(reac)

    thorpy.functions.playing(30,1000//parameters.FPS)
    m = thorpy.Menu(g,fps=parameters.FPS)
    m.play()

    app.quit()



##a->b: 0.01803719313101567
##b->c: 0.0775440644732113
##c->d: 0.7923680738645396
##d->e: 0.08457727400051168
##e->f: 0.014216953516080268
##f->g: 0.004750388631215161
##g->h: 0.01545287565724914
##h->j: 0.0016627215518888998
##j->k: 0.020678816337268535
##k->l: 0.4265509432993835
##l->m: 4.707531641103621
##m->n: 0.8678221897204471
##n->o: 2.3823143390489454
##o->p: 0.1551522771544694
##p->q: 0.4282461666100001
##q->z: 0.0019479672502016251

##    def refresh_display(self):
##        #in replay mode, sort according to length, not z!!!
####        self.objs.sort(key=lambda x:x.from_init.length(), reverse=True)
##        monitor.append("j")
##        self.objs.sort(key=lambda x:x.from_init.z, reverse=True)
##        monitor.append("k")
##        #
####        self.screen.fill((0,0,155))
##        self.screen.blit(self.background, (0,0))
##        self.screen.fill((0,200,0),self.screen_rect)
##        monitor.append("l")
##        #
##        self.track.refresh_and_draw_things(self.cam, self.light)
##        monitor.append("m")
##        for d in self.debris:
##            d.refresh()
##        monitor.append("n")
##        for obj in self.objs:
##            if obj.visible:
##                obj.refresh_and_draw(self.cam, self.light)
##        monitor.append("o")
##        #
##        self.hud.draw()
##        monitor.append("p")
##        if self.start_i >= 0:
##            self.show_start()
##        pygame.display.flip()
##        monitor.append("q")
##
##  def func_time(self):
##        monitor.append("a")
##        self.start_i = -1
##        self.i += 1
##        if self.start_i < 0:
##    ##        if self.i%10 == 0:
##    ##            if self.hero.colliding_with:
##    ##                print(self.hero.colliding_with.id)
##    ##            else:
##    ##                print("rien")
##            self.treat_commands()
##            monitor.append("b")
##            # dynamics
##            self.refresh_opponents()
##            monitor.append("c")
##            self.hero.dyn.refresh()
##            self.move_hero(self.hero.dyn.velocity)
##            monitor.append("d")
##            # collisions
##            self.obstacles_collisions()
##            monitor.append("e")
##            self.vessel_collisions()
##            monitor.append("f")
##            finisher = self.check_finish()
##            monitor.append("g")
##            if finisher:
##                finisher.finished = True
##                self.ranking.append(finisher)
##            # display
##            self.hide_useless_obstacles()
##            monitor.append("h")
##        self.refresh_display()
##        monitor.append("z")
##
##    def monitor(self):
##        monitor.show("abcdefghjklmnopqz")

##import time
##class Monitor:
##
##    def append(self, name):
##        if not hasattr(self, name):
##            setattr(self, name, [time.clock()])
##        else:
##            getattr(self,name).append(time.clock())
##
##    def show(self, letters):
##        tot = [0.]*len(letters)
##        L = len(getattr(self,letters[0]))
##        for i in range(1,len(letters)):
##            for k in range(L):
##                diff = getattr(self,letters[i])[k] - getattr(self,letters[i-1])[k]
##                tot[i] += diff
##        for i in range(1,len(tot)):
##            print(letters[i-1]+"->"+letters[i]+": "+str(tot[i]))
##
##monitor = Monitor()