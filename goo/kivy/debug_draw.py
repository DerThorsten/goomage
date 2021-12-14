import b2d
import numpy
from kivy.graphics import *



class KivyBatchDebugDraw(b2d.batch_debug_draw_cls(True, True, False)):

    def __init__(self, flags=None, alpha=0.5):
        super(KivyBatchDebugDraw,self).__init__()

        # what is drawn
        if flags is None:
            flags = ['shape','joint', 'particle']#,'aabb','pair','center_of_mass','particle']
        self.flags = flags
        self.clear_flags(['shape','joint','aabb','pair','center_of_mass','particle'])
        for flag in flags:
            self.append_flags(flag)

        self.alpha = alpha


    def draw_solid_polygons(self, points, sizes, colors):
        n_polygons = sizes.shape[0]
        start = 0
        for i in range(n_polygons):
            s = sizes[i]
            p = points[start:start+s,:]

            v = [] 
            indices = []
            for j in range(p.shape[0]):
                v.extend([p[j,0],p[j,1],0,0])
                indices.append(j)
            Mesh(vertices=v,indices=indices,mode='triangle_fan',color=Color(*colors[i,:],self.alpha))
            start += s

    def draw_polygons(self, points, sizes, colors):
        n_polygons = sizes.shape[0]
        start = 0
        for i in range(n_polygons):
            s = sizes[i]
            p = points[start:start+s,:]

            Line(points = points, close=True, width = 1,color=Color(*colors[i,:],self.alpha))

            start += s




    def draw_solid_circles(self, centers, radii, axis, colors):
        n = centers.shape[0]
        for i in range(n):
            radius = radii[i]
            center = centers[i,:]-radius
            size = ([radius*2,radius*2])
            e = Ellipse(pos=center,size=size,color=Color(*colors[i,:],self.alpha))
        
    def draw_circles(self, centers, radii, colors):
        n = centers.shape[0]
        for i in range(n):
            radius = radii[i]
            Line(circle = (centers[i,0],centers[i,1], radii[i]), width = 1, color=Color(*colors[i,:],self.alpha))
        

    def draw_points(self, centers, sizes, colors):
        pass

    def draw_segments(self, points, colors):
        n  = points.shape[0]
        for i in range(n):
            pass
            p =  points[i,0,0],points[i,0,1],points[i,1,0],points[i,1,1],
            Line(points=p, width=1.0, color=Color(*colors[i],self.alpha))

    def draw_particles(self, centers, radius, colors=None):
        default_color = (1,1,1,1)

        n_particles = centers.shape[0]
        centers -= radius
        d = 2 * radius
        size = (d, d)
        PushMatrix()
        Translate(-radius, -radius, 0)
        for i in range(n_particles):

            if colors is None:
                c = default_color
            else:
                c = colors[i,:]
            Rectangle(size=size, pos=centers[i,:],  color=Color(*c))
        PopMatrix()
