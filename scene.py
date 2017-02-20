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
        self.i = 0 #frame

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
        self.i += 1
        self.cam.move(V3(0,0,parameters.SPEED))
        self.refresh_screen()
        dyn = self.hero.dyn
        dyn.refresh()
        if self.cam.from_init.y < parameters.INITIAL_GROUND + parameters.YFLIGHT:
            if dyn.velocity.y < 0:
                dyn.velocity.y = 0
        self.cam.move(dyn.velocity)
        parameters.CAMPOS -= dyn.velocity
        parameters.GROUND += dyn.velocity.y
        press = pygame.key.get_pressed()
        if press[pygame.K_RIGHT]:
            new_x = self.hero.railx + 1
            if new_x < self.track.nx:
                pos = self.track.rails[new_x,self.hero.raily].pos.x
                if dyn.h.go_to(pos,self.i):
                    self.hero.railx += 1
        elif press[pygame.K_LEFT]:
            new_x = self.hero.railx - 1
            if new_x >= 0:
                pos = self.track.rails[new_x,self.hero.raily].pos.x
                if dyn.h.go_to(pos,self.i):
                    self.hero.railx -= 1
        elif press[pygame.K_DOWN]:
            dyn.v.restart(-1.)
        elif press[pygame.K_UP]:
            dyn.v.restart(1.)
        elif press[pygame.K_SPACE]:
            self.hero.rotate_around_center_z(DA)
        elif press[pygame.K_x]:
            self.race.init_scene(self)

    def refresh_cam(self):
        self.cam.objs = self.objs + self.track.get_all_objs()

    def move_hero(self, delta):
        self.cam.move(delta)
        self.hero.set_pos(parameters.HERO_POS)

    def set_hero_pos(self, pos):
        self.cam.move(pos)
        self.hero.set_pos(parameters.HERO_POS)

    def put_hero_on_rail(self, railx, raily, z=0):
        pos = self.track.rails[railx,raily].get_pos(z) + V3(self.track.railw//2,0,0)
        print("put hero", pos)
        self.set_hero_pos(pos)
        self.hero.railx = railx
        self.hero.raily = raily