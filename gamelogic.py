import random
import pygame
from pygame.math import Vector3 as V3
import thorpy
import parameters, drawing, light, camera
import alphabet


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


class Player:

    def __init__(self, name=None, color=None, money=1000, ranking=None):
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
        if ranking is None:
            self.ranking = random.randint(100,1000)

    def get_element(self):
        fs = thorpy.style.FONT_SIZE
        ename = thorpy.make_text(self.name,fs+4,(255,0,0))
        emoney = thorpy.make_text("Money: "+str(self.money))
        eranking = thorpy.make_text("Ranking: "+str(self.ranking))
        box = thorpy.Box.make([ename,emoney,eranking])
        return box


class ShowRanking:

    def __init__(self, title, ok_text, ranking):
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
        self.e_players = [p.get_element() for p in ranking]
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
        self.e_ok = get_eok(ok_text)
        self.e_bckgr.add_elements([self.e_viewport_frame,self.e_title,self.e_ok])
        m = thorpy.Menu(self.e_bckgr)
        m.play()


    def refresh_display(self):
        self.viewport.fill(self.viewport_color)
        for v in self.vessels:
            v.rotate_around_center_y(1)
            v.refresh_and_draw(self.cam,self.light)
        self.screen.blit(self.viewport,self.viewport_rect)
        pygame.display.update(self.viewport_rect)
