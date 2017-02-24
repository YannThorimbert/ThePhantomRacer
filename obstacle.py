from pygame.math import Vector3 as V3
import obstacle
import core3d, parameters


class Obstacle:

    def __init__(self, damage, x, y, z, obj):
        self.railx, self.raily, self.z = x, y, z
        self.obj = obj
        parameters.scene.objs.append(obj)
        obj.set_pos(parameters.scene.track.rails[x,y].get_middlepos(z))
        parameters.scene.track.obstacles.append(self)
        self.obj.compute_box3D()
        self.box = self.obj.box
        self.living = True
        self.damage = damage
        #
        self.movement = None
        self.rotation_x = None
        self.rotation_y = None

    def refresh(self):
        if self.rotation_x:
            self.obj.rotate_around_center_x(self.rotation_x)
        elif self.rotation_y:
            self.obj.rotate_around_center_y(self.rotation_y)
