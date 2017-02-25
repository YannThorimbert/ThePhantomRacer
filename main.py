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
import gamelogic

#si autres bugs d'affichages : if len(p) == len(thing.points): dans draw...

#be careful:
#   cam need to know all!!!! (for moving objects)

#faire un grep '#' pour checker qu'il y a pas de trucs importants qqpart

##OverflowError: signed short integer is greater than maximum
#       ==> si continue, faire comme pour Object3D avec control des val abs
#voir si refresh() de object 3d ferait pas mieux d'utiliser version GRU (cf refresh)


8.
#garage et stls

#----- 18 h

#TESTS SANDRINE!
#SONS

#qqch qui montre que on accelere (mouvement cam!)


# ##############################################################################
#parts:
    #wings : encore triangle
    #derive : (traduction?) ==> direct utiliser wings avec un material sans shadow!
    #engine : 2 types : cylindre, cube
# ##############################################################################


#nb opponents varie

#get_copy doit aussi copier from_initrot!!


def init_scene(scene): #debugging only
    #
##    import scenario
##    scenario.launch_intro_text()
##    scenario.launch_intro_text2()
##    scenario.launch_help()
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
    lg = levelgen.LevelGenerator(1000,3,3)
    rw,rh = parameters.RAILW,parameters.RAILH
    possible_obstacles = [primitivemeshes.p_rectangle(0.8*rw,0.8*rh,(0,0,255),(0,0,0))]
    lg.random_gen(nparts=4,objects=possible_obstacles,min_density=0.1,max_density=0.8)
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
    deco = trackdecorator.Decorator(track,track.zfinish//500)
    #
    finish = primitivemeshes.p_rectangle(track.railw,track.railh,(0,0,0))
##    for pos in track.rail_centers():
    for x in range(track.nx):
        for y in range(track.ny):
            pos = V3(track.rails[x,y].middlepos)
            pos.z = track.zfinish+5
            finish.set_pos(pos)
            if x%2 == 0:
                if y%2 == 0:
                    color = (0,0,0)
                else:
                    color = (255,255,255)
            else:
                if y%2 == 0:
                    color = (255,255,255)
                else:
                    color = (0,0,0)
            finish.set_color(Material(random.choice(color)))
            scene.objs.append(finish.get_copy())
    scene.track = track
    scene.opponents = [create_vessel(random.choice(drawing.colors)) for i in range(2)]
    scene.objs += scene.opponents
    import obstacle
    fin = Object3D("finish.stl")
    triangles = []
    for t in fin.triangles:
        isok = True
        for v in t.vertices():
            if v.y >= 0:
                isok = False
        if isok:
            triangles.append(t)
    from core3d import ManualObject3D
    fin = ManualObject3D(triangles)
    fin.rotate_around_center_x(-90)
    fin.scale(30.)
    fin.set_color(Material((255,255,0)))
    fin.move(V3(0,20,track.zfinish))
##    ob = obstacle.Obstacle(0., 0, 0, 100, fin)
    scene.objs += [fin]
    #
    scene.refresh_cam()
    hero_player = gamelogic.Player("Hero",Material(hero_color))
    hero.attach_to_player(hero_player)
    scene.players = [hero_player]
    for i,o in enumerate(scene.opponents):
        scene.put_opponent_on_rail(o,i+1,0,25)
        player = gamelogic.Player()
        o.attach_to_player(player)
        scene.players.append(player)
        o.set_ia(100, 0.01)
    hero.set_pos(parameters.HERO_POS)
    scene.put_hero_on_rail(0,0)
    print("end main")
    scene.refresh_vessels()
    hero.set_ia(100, 0.01)
    scene.hud.refresh_attributes()
    #
    gamelogic.ShowRanking("Start list", "Go to race", scene.players)




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
    gamelogic.ShowRanking("Ranking", "Go to garage",
                            scene.get_current_ranking_players())
    app.quit()


