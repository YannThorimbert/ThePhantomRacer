from pygame.math import Vector2 as V2
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

FPS = 40
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

objs = []

light_pos = V3(0,1000,-1000)
light_m = V3(20,20,20)
light_M = V3(200,200,200)
light = Light(light_pos, light_m, light_M)

fighter_color = V3(70,70,255)
wings = primitivemeshes.rectangle(5,2,fighter_color)
fighter = Object3D("meshes/f5.stl",more_triangles=wings.triangles)
for t in fighter.triangles:
    t.color = fighter_color
    t.ecolor = t.color
fighter.rotate_around_center_x(-90)
fighter.compute_box()
##fighter = fighter.get_splitted_copy(threshold=-2.5)
objs.append(fighter)




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
##track.add_thing(left, frompos=600, topos=1400, spacing=50, maxn=50)
##track.add_thing(right, 0, 800, 50, 4)
##track.add_thing(middle, 0, 1400, 50, 4)
track.add_thing(left, frompos=0, topos=1400, spacing=50, maxn=None)
track.add_thing(right, 0, 1400, 50, None)
track.add_thing(middle, 0, 1400, 50, None)

obstacle = primitivemeshes.cube(20, (255,0,0))
obstacle.set_pos(V3(0,track.y+10,200))
track.add_obstacle(obstacle)
obstacle.compute_box()
##print("cube points", obstacle.get_vertices())
##print("cube box", obstacle.box.points)



##poly = primitivemeshes.p_triangle(10.)
poly = primitivemeshes.p_disk(10.,filled=False,n=20)
##poly = primitivemeshes.p_arrow_line(20,100,20)
poly.move(V3(0,parameters.GROUND+parameters.YFLIGHT,250))
##poly.filled = True
objs.append(poly)

# ##############################################################################
FIGHTER_POS = V3(0,parameters.GROUND+parameters.YFLIGHT,20)
things_passed = 0

##opponent = fighter.get_copy()
##opponent.move(V3(-10,0,40))
opponents = [fighter.get_copy() for i in range(2)]
random.seed(3)
for o in opponents:
    o.move(V3(random.randint(-2,2)*10,random.randint(-2,2)*10, random.randint(4,6)*10))
    o.set_color(random.choice(drawing.colors))
objs += opponents

def refresh_screen():
    global things_passed
    fighter.set_pos(FIGHTER_POS)
##    poly.rotate_around_center_y(1)
    for o in opponents:
        o.move(V3(0,0,SPEED))
    objs.sort(key=lambda x:x.from_center.length(), reverse=True)
    screen.fill((255,255,255))
    screen.fill((0,255,0),thorpy.get_screen().get_rect().move((0,H//2)))
    track.refresh_and_draw_things(cam, light)
    for obj in objs: #pas boucler sur objs mais sur tous les triangles de la scen!!! ==> class scene, le concept de obj est la que pour user transfos ?
        if obj.visible:
            obj.refresh_and_draw(cam, light)
    for obs in track.get_nonthings():
        if obs.collide(fighter) or fighter.collide(obs):
            print("collision")
    pygame.display.flip()


SPEED = 1
def func_time():
    active_obj.move(V3(0,0,SPEED))
    refresh_screen()
    dyn.refresh()
    if cam.from_init.y < parameters.INITIAL_GROUND + parameters.YFLIGHT:
        if dyn.velocity.y < 0:
            dyn.velocity.y = 0
    active_obj.move(dyn.velocity)
##    parameters.CAMPOS += dyn.velocity
    parameters.GROUND += dyn.velocity.y
    press = pygame.key.get_pressed()
    if press[pygame.K_RIGHT]:
        dyn.h.restart(1.)
    elif press[pygame.K_LEFT]:
        dyn.h.restart(-1.)
    elif press[pygame.K_DOWN]:
        dyn.v.restart(-1.)
    elif press[pygame.K_UP]:
        dyn.v.restart(1.)
    elif press[pygame.K_SPACE]:
        fighter.rotate_around_center_z(DA)





##thorpy.application.SHOW_FPS = True


reac = thorpy.ConstantReaction(thorpy.THORPY_EVENT,func_time,
                                {"id":thorpy.constants.EVENT_TIME})

W,H = 800,600
app = thorpy.Application((W,H))
screen = thorpy.get_screen()

cam = Camera(screen, fov=512, d=2, objs=objs+track.get_all_objs())
objs += track.get_nonthings()
##cam.move(V3(0,20,0))

dyn = vessel.Dynamics(3., 0.1, 1., 0.1)

active_obj = cam

g = thorpy.Ghost.make()
g.add_reaction(reac)

##thorpy.application.SHOW_FPS = True

thorpy.functions.playing(30,1000//FPS)
m = thorpy.Menu(g,fps=FPS)
m.play()

app.quit()



