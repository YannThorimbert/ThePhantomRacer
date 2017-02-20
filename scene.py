from pygame.math import Vector3 as V3
import pygame
import thorpy
import parameters

class Scene:

    def __init__(self, race):
        self.light = None
        self.objs = []
        self.hero = None
        self.track = None
        self.opponents = None
        self.cam = None
        self.race = race
        self.screen = thorpy.get_screen()
        self.screen_rect = self.screen.get_rect().move((0,parameters.H//2))
        self.i = 0 #frame

    def refresh_screen(self):
    ##    poly.rotate_around_center_y(1)
        for o in self.opponents:
            o.move(V3(0,0,parameters.SPEED))
        self.objs.sort(key=lambda x:x.from_init.length(), reverse=True)
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
##        if self.i%10 == 0:
##            print(self.hero.railx, self.hero.raily)
        self.check_finish()
##        self.cam.move(V3(0,0,parameters.SPEED))
        self.move_hero(V3(0,0,parameters.SPEED))
        self.refresh_screen()
        dyn = self.hero.dyn
        dyn.refresh()
        if self.cam.from_init.y < 0:
            if dyn.velocity.y < 0:
                dyn.velocity.y = 0
        self.cam.move(dyn.velocity)
        press = pygame.key.get_pressed()
        if press[pygame.K_RIGHT]:
            new_x = self.hero.railx + 1
            if new_x < self.track.nx:
                newpos = self.track.rails[new_x,self.hero.raily].middlepos.x
                if dyn.h.go_to(newpos,self.i):
                    self.hero.railx += 1
        elif press[pygame.K_LEFT]:
            new_x = self.hero.railx - 1
            if new_x >= 0:
                newpos = self.track.rails[new_x,self.hero.raily].middlepos.x
                if dyn.h.go_to(newpos,self.i):
                    self.hero.railx -= 1
        if press[pygame.K_UP]:
            new_y = self.hero.raily + 1
            if new_y < self.track.ny:
                newpos = self.track.rails[self.hero.railx,new_y].middlepos.y
                if dyn.v.go_to(newpos,self.i):
                    self.hero.raily += 1
        elif press[pygame.K_DOWN]:
            new_y = self.hero.raily - 1
            if new_y >= 0:
                newpos = self.track.rails[self.hero.railx,new_y].middlepos.y
                if dyn.v.go_to(newpos,self.i):
                    self.hero.raily -= 1
        elif press[pygame.K_SPACE]:
            self.hero.rotate_around_center_z(1)
        elif press[pygame.K_x]:
            self.race.init_scene(Scene(self.race))
        self.obstacles_collisions()

    def refresh_cam(self):
        self.cam.objs = self.objs + self.track.get_all_objs()

    def move_hero(self, delta):
        self.cam.move(delta)
        self.hero.set_pos(parameters.HERO_POS)

    def set_hero_pos(self, pos):
        delta = pos - self.hero.from_init
        self.move_hero(delta)

    def mytrick(self):
        for obj in self.cam.objs:
            if obj is not self.hero:
                obj.move(V3(0,-8,0))


    def put_hero_on_rail(self, railx, raily, z=0):
        pos = self.track.rails[railx,raily].get_middlepos(z)
        print("put hero", pos)
##        pos.y += 8
        self.set_hero_pos(pos)
        self.hero.railx = railx
        self.hero.raily = raily

    def put_opponent_on_rail(self, opponent, railx, raily, z=0):
        pos = self.track.rails[railx,raily].middlepos
        pos = self.relative_to_cam(pos)
        pos.z = z
        print("put opponent", railx, raily, pos)
        opponent.set_pos(pos)
        opponent.railx = railx
        opponent.raily = raily

    def relative_to_cam(self, pos):
        return pos - self.cam.from_init

    def relative_to_hero(self, pos):
        return pos - self.cam.from_init + parameters.HERO_POS

    def absolute_hero_pos(self):
        return self.cam.from_init + parameters.HERO_POS

    def absolute_pos(self, pos):
        return self.cam.from_init + pos

    def check_finish(self):
        zfinish = self.track.zfinish - self.cam.from_init.z
        winners = []
        if self.hero.box.z[1] > zfinish:
            print("HERO FINISH")
            winners.append(self.hero)
        for o in self.opponents:
            if o.box.z[1] > zfinish:
                winners.append(o)
                print("OPPONENT FINISH")

    def obstacles_collisions(self):
        t = self.track
        for v in self.opponents+[self.hero]:
            for o in t.obstacles:
                z = o.box.z[0] <= v.box.z[1] <= o.box.z[1]
                if z:
                    x = o.box.x[0] <= v.box.x[1] <= o.box.x[1]
                    if x:
                        y = o.box.y[0] <= v.box.y[1] <= o.box.y[1]
                        if y:
                            ...
##                            print(self.i,"collision",v)
