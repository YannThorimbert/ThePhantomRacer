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
        #in replay mode, sort according to length, not z!!!
##        self.objs.sort(key=lambda x:x.from_init.length(), reverse=True)
        self.objs.sort(key=lambda x:x.from_init.z, reverse=True)
        self.screen.fill((0,0,155))
        self.screen.fill((0,200,0),self.screen_rect)
##        self.screen.fill((0,0,0))
        self.track.refresh_and_draw_things(self.cam, self.light)
        for obj in self.objs:
            if obj.visible:
                obj.refresh_and_draw(self.cam, self.light)
        pygame.display.flip()

    def treat_commands(self,dyn):
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
##            self.hero.rotate_around_center_z(1)
            dyn.velocity.z += self.hero.engine.on()
        elif press[pygame.K_x]:
            self.race.init_scene(Scene(self.race))

    def func_time(self):
        dyn = self.hero.dyn
        self.i += 1
        if self.i%100 == 0:
            pass
        self.check_finish()
        self.move_hero(V3(0,0,parameters.SPEED))
        self.refresh_screen()
        dyn.refresh()
        if self.cam.from_init.y < 0:
            if dyn.velocity.y < 0:
                dyn.velocity.y = 0
        self.treat_commands(dyn)
        #handle opponents ia
        for o in self.opponents:
            o.dyn.velocity.z += o.engine.on()
            o.move(o.dyn.velocity)
        self.cam.move(dyn.velocity)
        self.obstacles_collisions()
        self.hide_useless_obstacles()

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
                obj.move(V3(0,parameters.HERO_POS.y,0))


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
        for v in self.opponents+[self.hero]:
            for o in self.track.obstacles:
                if o.living:
                    z = o.box.z[0] <= v.box.z[1] <= o.box.z[1]
                    if z:
                        x1 = o.box.x[0] <= v.box.x[0] <= o.box.x[1]
                        x2 = o.box.x[0] <= v.box.x[1] <= o.box.x[1]
                        if x1 or x2:
                            y1 = o.box.y[0] <= v.box.y[0] <= o.box.y[1]
                            y2 = o.box.y[0] <= v.box.y[1] <= o.box.y[1]
                            if y1 or y2:
                                print(self.i,"collision",v)
                                v.handle_obstacle_collision(o)

    def hide_useless_obstacles(self):
        for o in self.track.obstacles:
            if o.living:
                if o.box.z[0] <= self.hero.box.z[1]:
                    o.obj.visible = False



