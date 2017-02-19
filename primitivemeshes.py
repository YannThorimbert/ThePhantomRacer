from core3d import ManualObject3D, Object3D, Triangle, Path3D
from pygame.math import Vector3 as V3

def rectangle(a,b,color=(0,0,0)):
    t1 = ManualObject3D([Triangle(V3(-a,0,0), V3(a,0,0), V3(a,b,0),
                                            color=V3(color)),
                            Triangle(V3(a,b,0), V3(-a,b,0), V3(-a,0,0),
                                            color=V3(color))])
    t1.refresh_normals()
    return t1

def triangle(a,color=(0,0,0)):
    t1 = ManualObject3D([Triangle(a*V3(-1,0,0), a*V3(1,0,0), a*V3(0,1,0),
                                            color=V3(color))])
    t1.refresh_normals()
    return t1

def cube(a, color=(0,0,0)):
    cube = Object3D("cube_ascii.stl")
    cube.scale(a)
    cube.refresh_normals()
    cube.set_color(V3(color))
    return cube

#path meshes "P"

class PathBuilder:

    def __init__(self, path):
        self.path = path

    def go(self, x,y,z):
        if len(self.path) == 0:
            self.path = [V3(x,y,z)]
        self.path.append(self.path[-1]+(x,y,z))

def p_triangle(a,filled=True,color=(0,0,0)):
    p = Path3D([V3(-a,0,0), V3(a,0), V3(0,a,0)], True, color)
    p.filled = filled
    return p

def p_disk(a,filled=True,color=(0,0,0),n=10):
    v0 = V3(a,0,0)
    path = [v0.rotate_z(angle) for angle in range(0, 360, 360//n)]
    p = Path3D(path, True, color)
    p.filled = filled
    return p

def p_arrow_line(a, b, c, color=(0,0,0)):
    path = PathBuilder([V3(-a,0,0)])
    path.go(2*a,0,0)
    path.go(0,0,b)
    path.go(c,0,0)
    path.go(-c-a,0,c)#middle
    path.go(-c-a,0,-c)
    path.go(c,0,0)
    path.go(0,0,-b)
    p = Path3D(path.path, True, color)
    p.filled = False
    return p

def p_line(frompos, topos, color=(0,0,0)):
    p = Path3D([frompos, topos], False, color)
    p.filled = False
    return p
