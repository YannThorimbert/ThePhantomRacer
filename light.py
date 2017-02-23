def interp_lin(f,m,M):
    return f*M + (1.-f)*m

def interp_quad(f,m,M):
    ff = f*f
    return (3.*ff - 2.*ff*f)*(M-m) + m

class Light:

    def __init__(self, pos, m, M):
        self.pos = pos
        self.m = m
        self.M = M
        self.interp_func = interp_quad

    def set_interpolation(mode):
        if "quad" in mode:
            self.interp_func = interp_quad
        elif "line" in mode:
            self.interp_func = interp_lin
        else:
            raise Exception("Unknown interpolation mode")

    def interp(self,f,m,M):
        return self.interp_func(f,m,M)

    def get_color_factor(self, t):
        line = t.c - self.pos
        angle = t.n.angle_to(line)
        return angle/180.


    def set_light(self, c, f):
        """Modify color c to reflect light exposition f."""
        if f > 0.5:
            f = (f-0.5)/0.5
            return self.interp(f,c,self.M)
        else:
            f = f/0.5
            return self.interp(f,self.m,c)

    def get_color(self, t):
        f = self.get_color_factor(t)
        return self.set_light(t.color, f)
