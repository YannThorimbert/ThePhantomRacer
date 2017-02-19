from pygame.math import Vector3 as V3
import pygame
import thorpy
import parameters

class Scene:

    def __init__(self, race):
        self.light = None
        self.objs = None
        self.hero = None
        self.track = None
        self.opponents = None
        self.cam = None
        self.race = race
        self.screen = thorpy.get_screen()
        self.screen_rect = self.screen.get_rect().move((0,parameters.H//2))

    def refresh_screen(self):
        self.hero.set_pos(parameters.HERO_POS)
    ##    poly.rotate_around_center_y(1)
        for o in self.opponents:
            o.move(V3(0,0,parameters.SPEED))
        self.objs.sort(key=lambda x:x.from_center.length(), reverse=True)
        self.screen.fill((255,255,255))
        self.screen.fill((0,255,0),self.screen_rect)
        self.track.refresh_and_draw_things(self.cam, self.light)
        for obj in self.objs: #pas boucler sur objs mais sur tous les triangles de la scen!!! ==> class scene, le concept de obj est la que pour user transfos ?
            if obj.visible:
                obj.refresh_and_draw(self.cam, self.light)
##        for obs in self.track.get_nonthings():
##            if obs.collide(self.hero) or self.hero.collide(obs):
##                print("collision")
        pygame.display.flip()

    def func_time(self):
        self.cam.move(V3(0,0,parameters.SPEED))
        self.refresh_screen()
        dyn = self.hero.dyn
        dyn.refresh()
        if self.cam.from_init.y < parameters.INITIAL_GROUND + parameters.YFLIGHT:
            if dyn.velocity.y < 0:
                dyn.velocity.y = 0
        self.cam.move(dyn.velocity)
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
            self.hero.rotate_around_center_z(DA)
        elif press[pygame.K_x]:
            self.race.init_scene(self)