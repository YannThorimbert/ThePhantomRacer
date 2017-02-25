from pygame.math import Vector3 as V3
import pygame

import thorpy
##from stlreader import Object3D #core3d vs stlreader ==> core un CHOUILLA mieux
from core3d import Object3D, Path3D
from light import Light, Material
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


6.
#si collision a basse vitesse, remet chacun sur un rail...

7.
#COURSE DEBUT A FIN

7.5
#pre-course et post-course

7.7
#scenar et menu

8.
#garage et stls

9.
#meilleure levelgen
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
##    from garage import Garage
##    garage = Garage()
##    garage.play()
    #
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
    hero_color = (70,70,255)
    def wings(a,b,color):
        return primitivemeshes.rectangle(a,b,color).triangles
    def create_vessel(color):
        v = vessel.Vessel("f5.stl",more_triangles=wings(5,1,color))
        v.rotate_around_center_x(-90)
        v.compute_box3D()
        v.set_color(Material(color))
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
    for o in track.obstacles:
        if random.random() < 0.4:
            if random.random() < 0.5:
                o.rotation_x = random.randint(2,5)* (2*random.randint(0,1) - 1)
            else:
                o.rotation_y = random.randint(2,5)* (2*random.randint(0,1) - 1)
            o.obj.set_color(Material(parameters.COLOR_ROTATING))
        if random.random() < 1.:
            r = random.random()
            if r < 0.2:
                o.movement_x = 1
            elif r < 0.4:
                o.movement_y = 1
            elif r < 0.5:
                o.movement_x = 1
                o.movement_y = 1
            if o.movement_x or o.movement_y:
                o.obj.set_color(Material(parameters.COLOR_MOVING))
    #
    import trackdecorator
    deco = trackdecorator.Decorator(track)
    #
    finish = primitivemeshes.rectangle(track.railw,track.railh,(0,255,0))
    for pos in track.rail_centers():
        pos.z = track.zfinish
        finish.set_pos(pos)
##        finish.set_color(random.choice(drawing.colors))
        scene.objs.append(finish.get_copy())
    scene.track = track
    scene.opponents = [create_vessel(random.choice(drawing.colors)) for i in range(2)]
    scene.objs += scene.opponents
    #
    scene.refresh_cam()
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
