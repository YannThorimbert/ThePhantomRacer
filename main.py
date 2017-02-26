from pygame.math import Vector3 as V3
import pygame

import thorpy
from core3d import Object3D, Path3D
from light import Light, Material
from camera import Camera
import primitivemeshes
import parameters
import drawing
import vessel
import random
from scene import Scene
import levelgen
import gamelogic
import garage
import trackdecorator
import obstacle
import scenario
from core3d import ManualObject3D

#remettre debris
#si autres bugs d'affichages : if len(p) == len(thing.points): dans draw...

#be careful:
#   cam need to know all!!!! (for moving objects)

#faire un grep '#' pour checker qu'il y a pas de trucs importants qqpart

##OverflowError: signed short integer is greater than maximum
#       ==> si continue, faire comme pour Object3D avec control des val abs
#voir si refresh() de object 3d ferait pas mieux d'utiliser version GRU (cf refresh)


#stocker toutes les pieces + set pour procedural
#structure de vaisseau procedural utilisant les pieces preloadees, avec class pour le materiau
#ajouter price dans parts



4.
#choisir vaisseau avec un Ranking et un fakePlayer

#wings au hasard - vaisseau au hasard (facile!) - au moment du choix, demander regenerer vaisseau

#sons


#qqch qui montre que on accelere (mouvement cam!)


# ##############################################################################
#parts:
    #wings : encore triangle
    #derive : (traduction?) ==> direct utiliser wings avec un material sans shadow!
    #engine : 2 types : cylindre, cube
# ##############################################################################


#nb opponents varie

#get_copy doit aussi copier from_initrot!!

#2pbs : fin

def create_vessel(color, model="BangDynamics"):
##    if not parameters.canonic_vessels:
##        garage.build_all_parts()
    wings = garage.wings_free(1.3,2.5,0.2,-0.5,1.,color,5.,y=0.)
    wings[0].rotate_around_center_x(90)
    wings[1].rotate_around_center_x(90)
    v = vessel.Vessel(model+".stl",more_triangles=wings[0].triangles+wings[1].triangles)
    v.set_color(Material(color))
    v.rotate_around_center_x(-90)
    garage.color_glasses(v,Material((0,0,0),M=(120,120,120)))
    v.rotate_around_center_y(-90)
    v.compute_box3D()
    v.compute_dynamics()
    v.from_init_rot = V3()
    return v

def init_game():
    parameters.players = [gamelogic.Player() for i in range(parameters.NPLAYERS-1)]
    hero_color = parameters.HERO_COLOR
    hero_player = gamelogic.Player(parameters.HERO_NAME,Material(hero_color))
    hero_player.points = 0
    parameters.player = hero_player
    parameters.players += [hero_player]
    hero = create_vessel(hero_color,model=parameters.HERO_MODEL)
    hero.is_hero = True
    hero.mass /= 2.
    hero.compute_dynamics()
    hero.name = "Hero" #!!
    hero.attach_to_player(hero_player,reset_color=False)

def init_scene():
##    random.seed(0)
    #
    gara = garage.Garage()
    gara.play()
    #
    parameters.scene = Scene()
    scene = parameters.scene
    scene.cam = Camera(scene.screen, fov=512, d=2, objs=[])
    scene.cam.set_aa(True)
    #
    light_pos = V3(0,1000,-1000)
    light_m = V3(20,20,20)
    light_M = V3(200,200,200)
    light = Light(light_pos, light_m, light_M)
    scene.light = light
    ##hero = hero.get_splitted_copy(threshold=-2.5)
    scene.hero = parameters.player.vessel
    hero = scene.hero
    scene.objs.append(hero)
    #track
    nx = random.randint(3,4)
    ny = random.randint(2,4)
    print("nx,ny",nx,ny)
    lg = levelgen.LevelGenerator(parameters.ZFINISH,nx,ny)
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
            if r < 0.1:
                o.movement_x = 1
            elif r < 0.2:
                o.movement_y = 1
            elif r < 0.25:
                o.movement_x = 1
                o.movement_y = 1
            if o.movement_x or o.movement_y:
                o.obj.set_color(Material(parameters.COLOR_MOVING))
    #

    deco = trackdecorator.Decorator(track,track.zfinish//500) #500
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
    scene.opponents = [create_vessel(random.choice(drawing.colors),random.choice(parameters.MODELS)) for i in range(2)]
    scene.objs += scene.opponents

##    fin = Object3D("finish.stl")
##    triangles = []
##    for t in fin.triangles:
##        isok = True
##        for v in t.vertices():
##            if v.y >= 0:
##                isok = False
##        if isok:
##            triangles.append(t)
##    fin = ManualObject3D(triangles)
##    fin.rotate_around_center_x(-90)
##    fin.scale(30.)
##    fin.set_color(Material((255,255,0)))
##    fin.move(V3(0,40,track.zfinish))
##    track.things_objects.append(fin)
##    scene.objs += [fin]
    #
    scene.refresh_cam()
    scene.players = [parameters.player]
    near = parameters.player.get_nearest_players()
    for i,o in enumerate(scene.opponents):
        player = near[i]
        scene.put_opponent_on_rail(o,i+1,0,25)
        o.attach_to_player(player)
        scene.players.append(player)
        o.set_ia(100, 0.01)
    hero.set_pos(parameters.HERO_POS)
    scene.put_hero_on_rail(0,0)
    print("end main")
    scene.refresh_vessels()
    scene.hud.refresh_attributes()
    g = gamelogic.ShowRanking("Start list", "Go to race", scene.players)
    return scene, g.goback



if __name__ == "__main__":
    app = thorpy.Application((parameters.W,parameters.H))
    ##    thorpy.application.SHOW_FPS = True
    screen = thorpy.get_screen()
    import dialog

    def launch_about():
        dialog.launch_blocking_alert("Credits",
        "Author: Yann Thorimbert\nLibraries used: Pygame, ThorPy (www.thorpy.org)",
        transp=False)
        e_bckgr.unblit_and_reblit()

    def play():
        def bru():
            thorpy.functions.quit_menu_func()
            e_bckgr.unblit_and_reblit()
##        varset = thorpy.VarSet()
##        varset.add("color", parameters.HERO_COLOR, "Choose vessel color:")
##        color = thorpy.ParamSetter.make([varset])
        name = thorpy.Inserter.make("Choose you name",value="Hero")
        box = thorpy.make_ok_box([name])
        box.e_ok.user_func = bru
        box.e_ok.user_params = {}
        box.center()
        scenario.launch(box)
        parameters.HERO_NAME = name.get_value()

        tit = thorpy.make_text("Choose vessel color")
        color = thorpy.ColorSetter.make("Choose vessel color")
        box = thorpy.make_ok_box([tit,color])
        box.e_ok.user_func = bru
        box.e_ok.user_params = {}
        box.center()
        scenario.launch(box)
        parameters.HERO_COLOR = color.get_value()
        print("setting", parameters.HERO_COLOR)
        #
        gamelogic.ShowRanking("Choose a vessel", "Continue", [], False, True)
        scenario.launch_intro_text()
        scenario.launch_intro_text2()
        scenario.launch_help()
        init_game()
        parameters.AA = vs.get_value("aa")
        parameters.VISIBILITY = vs.get_value("visibility")

        while True:
            while True:
                scene, goback = init_scene()
                if not goback:
                    break
            reac = thorpy.ConstantReaction(thorpy.THORPY_EVENT,scene.func_time,
                                            {"id":thorpy.constants.EVENT_TIME})
            g = thorpy.Ghost.make()
            parameters.ghost = g
            g.add_reaction(reac)
            thorpy.functions.playing(30,1000//parameters.FPS)
            m = thorpy.Menu(g,fps=parameters.FPS)
            m.play()
            gamelogic.ShowRanking("Ranking", "Go to garage",
                                    scene.get_current_ranking_players(),results=True)
            parameters.flush()
            if parameters.player.ranking == parameters.players[0].ranking:
                scenario.launch_end()


    e_title = thorpy.make_text("The Phantom Racer", 25, (255,0,0))

    e_play = thorpy.make_button("Start new game", play)
    e_disp,vs = gamelogic.get_display_options()
    e_font = thorpy.make_font_options_setter("./metadata", "Font options")
    e_about = thorpy.make_button("About", launch_about)
    e_quit = thorpy.make_button("Quit", thorpy.functions.quit_menu_func)
    elements = [e_title,e_play,e_disp,e_font,e_about,e_quit]
    background = thorpy.load_image("PaulinaRiva.png")
    background = thorpy.get_resized_image(background,
                                                    (parameters.W,parameters.H//2),
                                                    type_=max)
    e_bckgr = thorpy.Background.make(image=background,elements=elements)
    thorpy.store(e_bckgr)
    e_title.move((0,-50))
    m = thorpy.Menu(e_bckgr)
    m.play()

    app.quit()
