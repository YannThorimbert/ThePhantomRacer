from pygame.math import Vector3 as V3
import pygame

import thorpy
##from stlreader import Object3D #core3d vs stlreader ==> core un CHOUILLA mieux
from core3d import Object3D, Path3D, Box
from light import Light
from camera import Camera
import primitivemeshes
import parameters
import drawing
import vessel
import random
from track import Track
from scene import Scene
from race import Race

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
    objs = []
    parameters.refresh()
    #
    light_pos = V3(0,1000,-1000)
    light_m = V3(20,20,20)
    light_M = V3(200,200,200)
    light = Light(light_pos, light_m, light_M)
    scene.light = light
    #hero
    hero_color = V3(70,70,255)
    wings = primitivemeshes.rectangle(5,2,hero_color)
    hero = vessel.Vessel("f5.stl",more_triangles=wings.triangles)
    for t in hero.triangles:
        t.color = hero_color
        t.ecolor = t.color
    hero.rotate_around_center_x(-90)
    hero.compute_box()
    ##hero = hero.get_splitted_copy(threshold=-2.5)
    hero.dyn = vessel.Dynamics(3., 0.1, 1., 0.1)
    scene.hero = hero
    objs.append(hero)
    #track
    def get_thing(zpos, track):
        thing1 = primitivemeshes.triangle(2,(0,0,255))
        thing1.move(V3(track.x1,track.y,zpos))
        thing2 = primitivemeshes.triangle(2,(0,0,255))
        thing2.move(V3(track.x2,track.y,zpos))
        thing3 = primitivemeshes.p_line((track.x1,track.y,zpos),
                                        (track.x2,track.y,zpos), (0,0,255))
        return thing1, thing2, thing3
    track = Track(-40,40)
    left,right,middle = get_thing(0, track)
    track.add_thing(left, frompos=0, topos=1400, spacing=50, maxn=None)
    track.add_thing(right, 0, 1400, 50, None)
    track.add_thing(middle, 0, 1400, 50, None)
    scene.track = track
    #obstacles
    obstacle = primitivemeshes.cube(20, (255,0,0))
    obstacle.set_pos(V3(0,track.y+10,200))
    track.add_obstacle(obstacle)
    obstacle.compute_box()
    poly = primitivemeshes.p_disk(10.,filled=False,n=20)
    poly.move(V3(0,parameters.GROUND+parameters.YFLIGHT,250))
    objs.append(poly)
    #
    scene.opponents = [hero.get_copy() for i in range(2)]
    random.seed(3)
    for o in scene.opponents:
        o.move(V3(random.randint(-2,2)*10,random.randint(-2,2)*10, random.randint(4,6)*10))
        o.set_color(random.choice(drawing.colors))
    objs += scene.opponents
    scene.objs = objs
    scene.cam = Camera(scene.screen, fov=512, d=2, objs=objs+track.get_all_objs())
    scene.objs += track.get_nonthings()


if __name__ == "__main__":
    app = thorpy.Application((parameters.W,parameters.H))
    screen = thorpy.get_screen()

    ##cam.move(V3(0,20,0))

    g = thorpy.Ghost.make()


    ##thorpy.application.SHOW_FPS = True
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



