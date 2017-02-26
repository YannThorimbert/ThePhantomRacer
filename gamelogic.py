import random
import pygame
from pygame.math import Vector3 as V3
import thorpy
import parameters, drawing, light, camera
import alphabet, scenario


wordgen1 = alphabet.Dictionnary("thorn.txt","thorn_precisions.txt")
namel = 3
nameL = 8

def get_etitle(name,rect="screen"):
    e = thorpy.make_text(name,thorpy.style.FONT_SIZE+8,(255,255,0))
    e.stick_to(rect,"top","top")
    e.move((0,20))
    return e

def get_eok(name, rect="screen"):
    e = thorpy.make_button(name,thorpy.functions.quit_menu_func)
    e.stick_to(rect,"bottom","bottom")
    e.move((0,-20))
    return e

def refresh_ranking():
    parameters.players.sort(key=lambda x:x.points, reverse=True)
    for i,p in enumerate(parameters.players):
        p.ranking = i+1


def get_display_options():
    varset = thorpy.VarSet()
    varset.add("aa", True, "Anti-aliasing: ")
    varset.add("visibility", parameters.VISIBILITY, "Max display distance: ", [200,3000])
    e = thorpy.ParamSetterLauncher.make([varset], "Display options", "Display options")
    return e, varset

def launch_options():
    def func():
        parameters.scene.refresh_display()
        box.blit()
        pygame.display.flip()
    e, varset = get_display_options()
    e2 = thorpy.make_button("Show help",scenario.launch_help,{"func":func})
    def leave():
        if thorpy.launch_binary_choice("Are you sure?"):
            parameters.scene.abandon = True
        func()
    q = thorpy.make_button("Abandon",leave)
    box = thorpy.make_ok_box([thorpy.make_text("Pause"),thorpy.Line.make(100,"h"), e,e2,q])
    box.e_ok.user_func = thorpy.functions.quit_menu_func
    box.e_ok.user_params = {}
##    boxletter.set_main_color((200,200,200,50))
    box.set_main_color((200,200,255,200))
    box.center()
    scenario.launch(box)
    parameters.scene.cam.set_aa(varset.get_value("aa"))
    parameters.VISIBILITY = varset.get_value("visibility")


##    varset = thorpy.VarSet()
##    varset.add("name", name, "Name: ")
##    varset.add("type", ["Human","Beginner", "Normal", "Hard"],
##                            "Type: ")
##    color=(0,255,0) if name=="Player 1" else (0,0,255)
##    varset.add("color", color, "Color: ")
##    e = thorpy.ParamSetterLauncher.make([varset], name, name+" options")
##    return varset, e
##    ps = thorpy.ParamSetterLauncher()
##    e = thorpy.Box()


class Player:

    def __init__(self, name=None, color=None, money=1000, ranking=None, points=None):
        self.name = name
        if name is None:
            self.name =  wordgen1.genWord(random.randint(namel,nameL))
        #
        self.color = color
        if color is None:
            self.color = light.Material(random.choice(drawing.colors))
        self.money = money
        self.vessel = None
        self.ranking = ranking
        self.points = points
        if self.points is None:
            self.points = random.randint(0,parameters.NPLAYERS)

    def get_element(self,prename=""):
        fs = thorpy.style.FONT_SIZE
        ename = thorpy.make_text(prename+self.name,fs+4,(255,0,0))
        emoney = thorpy.make_text("Money: "+str(self.money))
        eranking = thorpy.make_text("Intergalactic Ranking: "+str(self.ranking))
        eranking = thorpy.make_text("Intergalactic Points: "+str(self.points))
        box = thorpy.Box.make([ename,emoney,eranking])
        return box

    def get_nearest_players(self):
        refresh_ranking()
        for i,p in enumerate(parameters.players):
            if p is self:
                print(i)
                if i == parameters.NPLAYERS-1:
                    p1 = parameters.players[i-2]
                    p2 = parameters.players[i-1]
                elif i == 0:
                    p1 = parameters.players[1]
                    p2 = parameters.players[2]
                else:
                    p1 = parameters.players[i-1]
                    p2 = parameters.players[i+1]
                assert p1 is not p2
                return p1,p2
        raise Exception("Couldnt find nearest players")


class ShowRanking:

    def __init__(self, title, ok_text, ranking, results=False, choosevessel=False):
        refresh_ranking()
         #
        light_pos = V3(0,1000,-1000)
        light_m = V3(20,20,20)
        light_M = V3(200,200,200)
        self.light = light.Light(light_pos, light_m, light_M)
        self.viewport = pygame.Surface((400,int(parameters.H*0.6)))
        self.viewport_color = (200,200,200)
        self.viewport.fill(self.viewport_color)
        self.viewport_rect = pygame.Rect((0,0),self.viewport.get_size())
        self.viewport_rect.centerx = parameters.W // 2 + 100
        self.viewport_rect.centery = parameters.H//2
        self.cam = camera.Camera(self.viewport, fov=512, d=2, objs=[])
        self.screen = thorpy.get_screen()
        #
        if results:
            ranking[0].points += 1
            ranking[0].money += 300 + (parameters.NPLAYERS-ranking[0].ranking)*100
            ranking[2].points -= 1
            ranking[2].money += 100
            ranking[1].money += 200
        #
        if choosevessel:
            self.e_players = []
            for kk in parameters.MODELS:
                def myfunc(mymodel):
                    parameters.HERO_MODEL = mymodel
                    print("setting model",mymodel)
                    thorpy.functions.quit_menu_func()
                b = thorpy.make_button(kk,myfunc,{"mymodel":kk})
                self.e_players.append(b)
            from main import create_vessel
            self.vessels = [create_vessel(parameters.HERO_COLOR,model) for model in parameters.MODELS]
        else:
            if results:
                self.e_players = [p.get_element(str(i+1)+") ") for i,p in enumerate(ranking)]
            else:
                self.e_players = [p.get_element() for i,p in enumerate(ranking)]
            self.vessels = [p.vessel.get_copy() for p in ranking]
        self.background = thorpy.load_image("background1.jpg")
        self.background = thorpy.get_resized_image(self.background,
                                                (parameters.W,parameters.H//2),
                                                type_=max)
        self.e_bckgr = thorpy.Background.make(image=self.background,
                                            elements=self.e_players)
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
        reaction =  thorpy.ConstantReaction(thorpy.THORPY_EVENT,
                                            self.refresh_display,
                                            {"id":thorpy.constants.EVENT_TIME})
        self.e_bckgr.add_reaction(reaction)
        for i,v in enumerate(self.vessels):
            pos = self.e_players[i].get_fus_rect().center
            v.set_pos(V3(0,-i*4.5,20))
            v.move(V3(0,4,0))
        #
        thorpy.store(self.e_bckgr,gap=40)
        for e in self.e_players:
            e.stick_to(self.viewport_rect,"left","right",align=False)
            e.move((-5,0))
        self.e_title = get_etitle(title)
        if not choosevessel:
            self.e_ok = get_eok(ok_text)
            self.e_bckgr.add_elements([self.e_viewport_frame,self.e_title,self.e_ok])
        else:
            self.e_bckgr.add_elements([self.e_viewport_frame,self.e_title])
        self.goback = False
        def return_garage():
            self.goback=True
            thorpy.functions.quit_menu_func()
        if not results and not choosevessel:
            self.e_back = thorpy.make_button("Return to garage", return_garage)
            self.e_back.stick_to(self.e_ok, "left", "right")
            self.e_back.move((-20,0))
            self.e_bckgr.add_elements([self.e_back])
        m = thorpy.Menu(self.e_bckgr)
        m.play()


    def refresh_display(self):
        self.viewport.fill(self.viewport_color)
        for v in self.vessels:
            v.rotate_around_center_y(1)
            v.refresh_and_draw(self.cam,self.light)
        self.screen.blit(self.viewport,self.viewport_rect)
        pygame.display.update(self.viewport_rect)
