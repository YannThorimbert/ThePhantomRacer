import random

import parameters
import track
import obstacle

class LevelGenerator:

    def __init__(self, zfinish, nx, ny):
        self.zfinish = zfinish
        self.nx = nx
        self.ny = ny
        self.track = track.Track(zfinish,nx,ny)
        parameters.scene.track = self.track

    def add_static_obstacles(self, density, objects):
        """Density: average number of obstacles per 100 m"""
        n = density * self.zfinish / 100.
        done = set([])
        i = 0
        while i < n:
            x = random.randint(0,self.nx-1)
            y = random.randint(0,self.ny-1)
            z = random.randint(0,self.zfinish)
            if (x,y,z) not in done:
                done.add((x,y,z))
                obj = random.choice(objects).get_copy()
                obstacle.Obstacle(x,y,z,obj)
                i += 1
        print("obstacles:",done)
