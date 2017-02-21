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
##from track import Track
##from obstacle import Obstacle
import levelgen

#be careful:
#   cam need to know all!!!!

##OverflowError: signed short integer is greater than maximum
#       ==> si continue, faire comme pour Object3D avec control des val abs

2.
#tordre vitesse plutot que ajouter. Preserver norme.
#vitesse de virage ~ norme (en + de vitesse intrinseque)

3.
#collisions - empecher la superposition. Check collisions que avec obstacles!!! entre opponents, gerer AVANT changement de rails...

4.
#IA

5.
#meilleure levelgen

6.
#course complete


# ##############################################################################
#parts:
    #wings
    #derive (traduction?)
    #nose
    #engine (tail)
    #cockpit
#tester la forme la moins bugesque entre section ~cubique et ~triangle
# ##############################################################################

#multilights!
#deco sur les bords sont des sources. Possedent des couleurs. Clignotent.
#ne pas faire de rendu au-dela de visibility !
#trier les things !!!!
#blit visibility VS max_n_parts?
#kill z < 0 ? Si on veut faire de beaux replay avec vue libre, il faut que le maxn du manager soit toujours egal a n.
#tourner : conserver la norme de la vitesse (==> reduction vitesse selon z)

#opti: utiliser les dist au carre. Pygame vs math vs manuel
#opti: angles peuvent etre precomputes. normales sont normalizees qu'une fois au tout debut
#camera: quatre fonctions, correspondant (antialias, light)
#chaque objet a un facteur k et blit que de 0 a k


#remettre les things devant au fur et a mesure pour perf

#mouvements verticaux aussi !!!!

#path3D : gfx filled polygon! ==> propriete filled

#collisions spheriques au debut en tout cas? non tester box
#nb opponents: 0, 1, 3 ?

#magma: body a un attribut force, et collisions de spheres toutes simples...

#FIGNOLING:
#si collision, alors regarde quelle partie du vaisseau, puis l'enleve et dessine les parties subdivisees qui volent en eclats



def init_scene(scene): #debugging only
    parameters.scene = scene
    random.seed(3)
    parameters.scene = scene
    scene.cam = Camera(scene.screen, fov=512, d=2, objs=[])
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
        v.dyn = vessel.Dynamics(1,1,v)
        return v
    hero = create_vessel(hero_color)
    hero.engine.force *= 2
    ##hero = hero.get_splitted_copy(threshold=-2.5)
    scene.hero = hero
    scene.objs.append(hero)
    #track
##    track = Track(12,12,zfinish=1000,nx=3,ny=2)
    lg = levelgen.LevelGenerator(3000,3,2)
    rw,rh = parameters.RAILW,parameters.RAILH
    possible_obstacles = [primitivemeshes.rectangle(0.8*rw,0.8*rh,(0,255,255))]
##    possible_obstacles = [primitivemeshes.rectangle(0.8*rw,0.8*rh,(0,255,255)),
##                            primitivemeshes.cube(0.8*rw/2.,(255,0,0))]
    lg.add_static_obstacles(1,possible_obstacles)
    track = scene.track
    #obstacles
##    Obstacle(1,0,200,primitivemeshes.cube(track.railw//2, (255,0,0)))
##    Obstacle(0,0,50,primitivemeshes.rectangle(track.railw,track.railh,(0,0,255)))
##    Obstacle(1,0,110,primitivemeshes.rectangle(track.railw,track.railh,(0,255,255)))
##    Obstacle(0,0,800,primitivemeshes.rectangle(track.railw,track.railh,(0,255,255)))
    #
    track.add_visual_rails()
    finish = primitivemeshes.rectangle(track.railw,track.railh,(0,255,0))
    for pos in track.rail_centers():
        pos.z = track.zfinish
        finish.set_pos(pos)
        finish.set_color(random.choice(drawing.colors))
        scene.objs.append(finish.get_copy())
    scene.track = track
    scene.opponents = [create_vessel(random.choice(drawing.colors)) for i in range(1)]
    scene.objs += scene.opponents
    #
    scene.refresh_cam()
##    scene.init_cam()
    scene.put_hero_on_rail(0,0)
    for i,o in enumerate(scene.opponents):
        scene.put_opponent_on_rail(o,i+1,0,25)
    scene.mytrick()



if __name__ == "__main__":
    app = thorpy.Application((parameters.W,parameters.H))
    screen = thorpy.get_screen()
    ##cam.move(V3(0,20,0))
    g = thorpy.Ghost.make()

    thorpy.application.SHOW_FPS = True
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



