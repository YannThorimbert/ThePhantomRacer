from pygame.math import Vector3 as V3
import drawing

class Camera:

    def __init__(self, screen, fov, d, objs):
        self.screen = screen
        self.w = screen.get_width()/2.
        self.h = screen.get_height()/2.
        self.fov = fov
        self.d = d
        self.objs = objs
        self.aa = True
        if self.aa:
            self.draw_object = drawing.draw_aa
            self.draw_filled_polygon = drawing.draw_filled_polygon_aa
            self.draw_polygon = drawing.draw_polygon_aa
##            self.draw_path = drawing.draw_lines_aa
            self.draw_path = drawing.draw_lines_normal
        else:
            self.draw_object = drawing.draw_normal
            self.draw_filled_polygon = drawing.draw_filled_polygon_normal
            self.draw_polygon = drawing.draw_polygon_aa
            self.draw_path = drawing.draw_lines_normal
        self.from_init = V3()

    def set_aa(self, aa):
        self.aa = True
        if self.aa:
            self.draw_object = drawing.draw_aa
        else:
            self.draw_object = drawing.draw_normal

    def project(self, v): #perspective projection
        denom = self.d + v.z
        if denom < 1:
            denom = 1
        factor = self.fov / denom
        x = v.x * factor + self.w
        y = -v.y * factor + self.h
        return x, y

    def move(self, delta):
        self.from_init += delta
        delta *= -1.
        for o in self.objs:
            o.move(delta)

    def rotate(self, axis, angle): #a optimiser
        angle *= -1.
        func = "rotate_"+axis
        for o in self.objs:
            getattr(o,func)(angle)