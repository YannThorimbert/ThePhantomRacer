import thorpy

import parameters



class HUD:

    def __init__(self):
        self.hfull = thorpy.load_image("heart_full.png",(255,255,255))
        self.hempty = thorpy.load_image("heart_empty.png",(255,255,255))
        self.heart_size = self.hfull.get_size()
        self.heart_spacing = self.heart_size[0] + 5
        self.xlife = - self.heart_spacing + 5
        self.ylife = 5
        #
        self.e_speed = thorpy.make_text("0 km/h",
                                        thorpy.style.FONT_SIZE+8, (255,255,0))
        self.e_speed.stick_to("screen","top","top")
        self.e_speed.stick_to("screen","right","right",False)
        self.e_speed.move((-50,5))
        #
        self.screen = thorpy.get_screen()
        self.scene = None
        self.hero = None

    def refresh_attributes(self):
        self.scene = parameters.scene
        self.hero = parameters.scene.hero

    def draw_life(self):
        x = 0
        for i in range(self.hero.life):
            x += self.heart_spacing
            self.screen.blit(self.hfull,(self.xlife+x,self.ylife))
        for i in range(self.hero.max_life - self.hero.life):
            x += self.heart_spacing
            self.screen.blit(self.hempty,(self.xlife+x,self.ylife))
        vel = int(self.hero.dyn.velocity.z*parameters.SPEED_HUD)
        if self.e_speed.get_text() != vel:
            self.e_speed.set_text(str(vel)+" km/h")
        self.e_speed.blit()
