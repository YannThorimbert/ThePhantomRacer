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

#be careful:
#   cam need to know all!!!! (for moving objects)

#faire un grep '#' pour checker qu'il y a pas de trucs importants qqpart

##OverflowError: signed short integer is greater than maximum
#       ==> si continue, faire comme pour Object3D avec control des val abs


#voir si refresh() de object 3d ferait pas mieux d'utiliser version GRU (cf refresh)

4.
#IA

4.5
#damage collisions

5.
#meilleure levelgen

6.
#course complete

7.
#garage

8.
#monitoring temps cpu

10.
#rotation en virage. hero_pos.z change avec la vitesse!

11.
#mod collision ==> explosions (==> parachute si le temps)



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

#deco sur les bords sont des sources de lumière?. En tout cas possedent des couleurs. Clignotent.

#trier les things 1 fois!!!!

#opti: utiliser les dist au carre. Pygame vs math vs manuel

#opti: chaque objet a un facteur k et blit que de 0 a k

#nb opponents: 0, 1, 3 ? ==> varie

def init_scene(scene): #debugging only
    parameters.scene = scene
    random.seed(3)
    parameters.scene = scene
    scene.cam = Camera(scene.screen, fov=512, d=2, objs=[])
    scene.cam.set_aa(False)
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
    #
    track.add_visual_rails()
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
    hero.set_pos(parameters.HERO_POS)
    print("caca", hero.from_init)
    scene.put_hero_on_rail(0,0)
##    scene.mytrick()
    print("end main")
    scene.refresh_vessels()
    hero.set_ia(100, 0.01)



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



