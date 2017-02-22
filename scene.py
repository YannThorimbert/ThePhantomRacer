from pygame.math import Vector3 as V3
import pygame
import thorpy
import parameters, vessel

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


    def treat_commands(self): #a unifier (facile) et utiliser dans collisions
        press = pygame.key.get_pressed()
        if press[pygame.K_RIGHT]:
            self.hero.change_rail(1,0)
        elif press[pygame.K_LEFT]:
            self.hero.change_rail(-1,0)
        if press[pygame.K_UP]:
            self.hero.change_rail(0,1)
        elif press[pygame.K_DOWN]:
            self.hero.change_rail(0,-1)
        elif press[pygame.K_SPACE]:
##            self.hero.rotate_around_center_z(1)
            self.hero.boost()
        elif press[pygame.K_x]:
            self.race.init_scene(Scene(self.race))

    def func_time(self):
        self.i += 1
##        if self.i%10 == 0:
##            print(self.hero.raily)
        self.check_finish()
        self.move_hero(V3(0,0,parameters.SPEED))
        self.refresh_screen()
        self.hero.dyn.refresh()
        if self.cam.from_init.y < 0:
            if dyn.velocity.y < 0:
                dyn.velocity.y = 0
        self.treat_commands()
        for o in self.opponents + [self.hero]: #stocker 1 fois pour toutes
            for o2 in self.opponents + [self.hero]:
                if o.should_collide(o2):
                    vessel.collision(o,o2)
        for o in self.opponents:
            #handle opponents ia here
##            ia.play(o)
            o.boost() #goes into ia
            o.dyn.refresh()
            o.move(o.dyn.velocity)
        self.cam.move(self.hero.dyn.velocity)
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
                    if o.box.collide(v.box):
                        print(self.i,"collision",v)
                        v.obstacle_collision(o)


    def hide_useless_obstacles(self):
        for o in self.track.obstacles:
            if o.living:
                if o.box.z[0] <= self.hero.box.z[1]:
                    o.obj.visible = False



