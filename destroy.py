import parameters, physics, random



class Destroy: #doesnt work with Path3D

    def __init__(self, obj):
        self.obj = obj
        if len(self.obj.triangles) < parameters.N_DESTROY:
            while len(self.obj.triangles):
                self.obj = self.obj.get_splitted_copy(refresh_normals=False,
                                                        threshold=0.5)
            self.obj.refresh_normals()
        for t in self.obj.triangles:
            setattr(t, "physics", physics.Physics())


    def start(self, pos, vel):
        self.obj.set_pos(pos)
        for t in self.obj.triangles:
            t.vel = random
            t.rot = random

    def refresh(self):
        for t in self.obj.triangles:
            t.move(t.vel)
            t.rotate(t.rot)