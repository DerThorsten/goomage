
from b2d.testbed import TestbedBase
import random
import numpy as np
import b2d 
import math
import networkx
from functools import partial
from enum import Enum


from .utils import *
from .query import *
from .kivy.textures import images
from .kivy.draw_utils import *


from kivy.graphics import *
from kivy.core.image import Image


def query_goo_placement(root, pos):
    goo_cls = root.goo_cls

    n  = root.level.goo_contigent[root.goo_cls]
    if n <= 0:
        return InsertInfo(InsertType.CANNOT_INSERT) 

    def filter_func(bdy):
        goo = bdy.user_data
        if isinstance(goo, GooBase) and \
           goo.can_connect_with_cls(root.goo_cls) and \
           goo.has_free_connection():
           return True
        return False
    bodies = bodies_in_radius(root.world, pos=pos, radius=root.goo_cls.discover_radius,
                                filter_func=filter_func, max_elements=10)
    goos = [b.user_data for b in bodies]
    n_goos = len(goos)

    
    if n_goos >= 2 and goo_cls.can_be_inserted_as_joint:

        # insert as joint?
        def distance(a,b, p):
            if root.goo_graph.has_edge(a[0], b[0]):
                return float('inf')
            return  np.linalg.norm((a[1] + b[1])/2 - p)

        i,j,best_dist = best_pairwise_distance(goos, 
            f= lambda goo: (goo,np.array(goo.body.position)),
            distance=partial(distance, p=pos))

        if best_dist < 0.5:
            return InsertInfo(InsertType.AS_JOINT,
                goos=(goos[i],goos[j]))     
    
    if n_goos >= goo_cls.min_connect and  goo_cls.can_be_inserted_as_body:

        assert goo_cls.min_connect == goo_cls.max_connect
        assert goo_cls.min_connect in [1,2]
        n_connect = goo_cls.min_connect

        if n_connect == 2:

            # insert as body?
            f = lambda goo :  (goo, (goo.body.position- b2d.vec2(pos)).length)

            def distance(a,b):
                if not root.goo_graph.has_edge(a[0], b[0]):
                    return float('inf')
                return (a[1] + b[1])

            i,j,best_dist = best_pairwise_distance(goos, f=f, distance=distance)

            if best_dist < 1000:
                return InsertInfo(InsertType.AS_GOO, goos=(goos[i], goos[j]))

        if n_connect == 1:
            f = lambda goo :   (goo.body.position- b2d.vec2(pos)).length
            distances = [f(goo) for goo in goos]
            distances.sort()


    return InsertInfo(InsertType.CANNOT_INSERT)


class InsertType(Enum):
    AS_GOO = 1
    AS_JOINT = 2
    CANNOT_INSERT = 3


class InsertInfo(object):
    def __init__(self, insert_type, **info):
        self.insert_type = insert_type
        self.info = info

class GooBase(object):

    can_be_inserted_as_joint = True
    can_be_inserted_as_body = True
    discover_radius = 10
    max_degree = 100
    min_degree = 2



    min_connect = 2
    max_connect = 2 

    def __init__(self, root, body):
        self.root = root
        self.body = body
        self.buffs = []


    @classmethod
    def connect_goos(cls, root, goo_a, goo_b):
        graph = root.goo_graph
        world = root.world
        body_a = goo_a.body
        body_b = goo_b.body

        length = (body_a.position - body_b.position).length

        j =  world.create_distance_joint(body_a,body_b, 
            length=length,
            stiffness=300,
            collide_connected=True
        )
        graph.add_edge(goo_a, goo_b,joint=j)
        return j


    @classmethod
    def can_connect_with_cls(cls, other_cls):
        return True

    @property
    def degree(self):
        return self.root.goo_graph.degree(self)

    def has_free_connection(self):
        d = self.degree
        return d >= self.min_degree and d < self.max_degree

    @classmethod
    def kivy_draw_tentative(cls, root, position, insert_info):
        insert_type = insert_info.insert_type
        alpha = 0.5
        if insert_type == InsertType.AS_GOO:

            Line(points=[position, tuple(insert_info.info['goos'][0].body.position)], 
                width=0.15, color=Color(0.5,0.5,1,alpha))
            Line(points=[position, tuple(insert_info.info['goos'][1].body.position)], 
                width=0.15, color=Color(0.5,0.5,1,alpha))
            cls.draw_goo(position=position, angle=None)

        elif insert_type == InsertType.AS_JOINT:
            Line(points=[
                    tuple(insert_info.info['goos'][1].body.position), 
                    tuple(insert_info.info['goos'][0].body.position)
                ], 
                width=0.15, color=Color(0.5,0.5,1,alpha))
    @classmethod
    def draw_joint(cls, pos_a, pos_b):
        Line(points=[tuple(pos_a), tuple(pos_b)], 
                width=0.15, color=Color(0.5,0.5,1,1))

    def draw(self):
        self.draw_goo(
            position=self.body.position, 
            angle=self.body.angle)

    def pre_step(self, dt, pass_nr):
        pass

    def remove_buffs(self):
        for buff in self.buffs:
            buff.remove()


    @classmethod
    def query_placement(cls, root, position, query_only):
        
        def filter_func(bdy):
            goo = bdy.user_data
            if isinstance(goo, GooBase) and \
               goo.can_connect_with_cls(root.goo_cls) and \
               goo.has_free_connection():
               return True
            return False
        bodies = bodies_in_radius(root.world, pos=position, radius=cls.discover_radius,
                                    filter_func=filter_func, max_elements=10)
        goos = [b.user_data for b in bodies]
        n_goos = len(goos)

        print(n_goos)

        if n_goos >= 2:

            # insert as joint?
            def distance(a,b, p):
                if root.goo_graph.has_edge(a[0], b[0]):
                    return float('inf')
                return  np.linalg.norm((a[1] + b[1])/2 - p)

            i,j,best_dist = best_pairwise_distance(goos, 
                f= lambda goo: (goo,np.array(goo.body.position)),
            distance=partial(distance, p=position))

            if best_dist < 0.5:
                
                draw_callback = partial(cls.draw_joint, 
                    pos_a=goos[i].body.position,
                    pos_b=goos[j].body.position,
                )
                def insert_callack():
                    root.level.goo_contigent[cls] -= 1
                    root.hud.set_amount(cls, root.level.goo_contigent[cls] )
                    cls.connect_goos(root, goos[i], goos[j])

                return True, draw_callback, insert_callack




            # insert as body?
            f = lambda goo :  (goo, (goo.body.position- b2d.vec2(position)).length)

            def distance(a,b):
                if not root.goo_graph.has_edge(a[0], b[0]):
                    return float('inf')
                return (a[1] + b[1])

            i,j,best_dist = best_pairwise_distance(goos, f=f, distance=distance)

            if best_dist < 1000:
                def draw_callback():
                    cls.draw_joint(pos_a=position, pos_b=goos[i].body.position)
                    cls.draw_joint(pos_a=position, pos_b=goos[j].body.position)
                    cls.draw_goo(position=position, angle=None)

                def insert_callack():
                    goo = cls.create(root=root, position=position)
                    root.level.goo_contigent[cls] -= 1
                    root.hud.set_amount(cls, root.level.goo_contigent[cls] )

                    cls.connect_goos(root, goo, goos[i])
                    cls.connect_goos(root, goo, goos[j])

                return True, draw_callback, insert_callack



        return False, None, None



class PlainGoo(GooBase):

    can_be_inserted_as_joint = True
    texture_path = "goo/art/plain_goo_100x100.png"
    texture = Image(texture_path)
    radius = 0.75



    @classmethod
    def draw_goo(cls, position, angle):
        size = (cls.radius*2, cls.radius*2)
        pos = list(position)
        pos[0] -= cls.radius
        pos[1] -= cls.radius

        textured_rect(pos, size, cls.texture, angle, rot_origin=list(position))

    @classmethod
    def create(cls, root, position):
        world = root.world

        shape = b2d.circle_shape(radius=PlainGoo.radius)
        fixture = b2d.fixture_def(shape=shape, density=1, friction=0.2)
        body = world.create_dynamic_body(
            position=position, 
            fixtures=fixture,
            linear_damping=0.2,
            angular_damping=0.9
        )
        goo = PlainGoo(root, body)
        root.goo_graph.add_node(goo)
        body.user_data = goo

        return goo

    def __init__(self, root, body):
        super(PlainGoo, self).__init__(root=root, body=body)

class AnchorGoo(GooBase):
    texture_path = "goo/art/anchor_goo_100x100.png"
    texture = Image(texture_path)

    can_be_inserted_as_joint = False

    radius = 0.75
    density = 100

    def __init__(self, root, body):
        super(AnchorGoo, self).__init__(root=root, body=body)

    @classmethod
    def create(cls, root, position):
        world = root.world

        shape = b2d.polygon_shape(box=[AnchorGoo.radius,AnchorGoo.radius])
        fixture = b2d.fixture_def(shape=shape, density=AnchorGoo.density, friction=0.2)
        body = world.create_dynamic_body(
            position=position, 
            fixtures=fixture,
            linear_damping=0.2,
            angular_damping=0.9
        )
        goo = AnchorGoo(root, body)
        body.user_data = goo
        root.goo_graph.add_node(goo)
        return goo

    @classmethod
    def draw_goo(cls, position, angle):
        size = (AnchorGoo.radius*2, AnchorGoo.radius*2)
        pos = list(position)
        pos[0] -= AnchorGoo.radius
        pos[1] -= AnchorGoo.radius

        textured_rect(pos, size, cls.texture, angle, rot_origin=list(position))



    @classmethod
    def connect_goos(cls, root, goo_a, goo_b):
        graph = root.goo_graph
        world = root.world
        body_a = goo_a.body
        body_b = goo_b.body

        length = (body_a.position - body_b.position).length

        j =  world.create_distance_joint(body_a,body_b, 
            length=length,
            stiffness=20000.0,
            collide_connected=True,
            # max_length=cls.rope_length
        )
        graph.add_edge(goo_a, goo_b,joint=j)
        return j


class MagicGoo(GooBase):
    can_be_inserted_as_joint = False

    texture_path = "goo/art/magic_goo_150x190.png"
    texture = Image(texture_path)
    radius = 0.75
    aura_radius = 15 * radius

    class Buff(object):
        def __init__(self, target_goo):
            self.target_goo = target_goo
            self.orginal_gravity_scale = self.target_goo.body.gravity_scale
            if self.orginal_gravity_scale > 0:
                self.target_goo.body.gravity_scale = self.orginal_gravity_scale * 0.1
            else:
                self.target_goo.body.gravity_scale = self.orginal_gravity_scale * 1.2
                # print(self.target_goo.body.gravity_scale)

        def remove(self):
            self.target_goo.body.gravity_scale = self.orginal_gravity_scale

    @classmethod
    def draw_goo(cls, position, angle):
        size = (cls.radius*2 * 1.5, cls.radius*2 * 1.9)
        pos = list(position)
        pos[0] -= cls.radius * 1.6
        pos[1] -= cls.radius

        aura_factor = 15
        # outline
        Line(circle = (*position, cls.aura_radius), width = 0.1, color=Color(1,0.5,1,0.1))

        # filled circle
        aura_size = (cls.aura_radius*2 , cls.aura_radius*2 )
        aura_pos = list(position)
        aura_pos[0] -= cls.aura_radius 
        aura_pos[1] -= cls.aura_radius
        e = Ellipse(pos=aura_pos,size=aura_size,color=Color(1,1,1,0.1))

        textured_rect(pos, size, cls.texture, angle, rot_origin=list(position))


    @classmethod
    def create(cls, root, position):
        world = root.world

        shape = b2d.circle_shape(radius=cls.radius)
        fixture = b2d.fixture_def(shape=shape, density=1, friction=0.2)
        body = world.create_dynamic_body(
            position=position, 
            fixtures=fixture,
            linear_damping=0.2,
            angular_damping=0.9
        )
        goo = cls(root, body)
        root.goo_graph.add_node(goo)
        body.user_data = goo

        return goo

    def pre_step(self, dt, pass_nr):
        if pass_nr == 0:
            root = self.root

            pos = self.body.position


            def filter_func(bdy):
                goo = bdy.user_data
                if isinstance(goo, GooBase) and  goo != self:
                   return True
                return False


            bodies = bodies_in_radius(root.world, pos=pos, radius=root.goo_cls.discover_radius,
                                        filter_func=filter_func, max_elements=float('inf'))
            for body in bodies:
                goo = body.user_data
                print(f"installed buff on {goo}.__cls__")
                goo.buffs.append(MagicGoo.Buff(target_goo=goo))

    def __init__(self, root, body):
        super(MagicGoo, self).__init__(root=root, body=body)

class BaloonGoo(GooBase):
    texture_path = "goo/art/ballon_goo_100x110.png"
    texture = Image(texture_path)
    radius = 0.75
    max_degree = 1
    min_degree = 1

    min_connect = 1
    max_connect = 1
    can_be_inserted_as_joint = False
    rope_length = 10

    @classmethod
    def connect_goos(cls, root, goo_a, goo_b):
        graph = root.goo_graph
        world = root.world
        body_a = goo_a.body
        body_b = goo_b.body

        # length = (body_a.position - body_b.position).length

        j =  world.create_distance_joint(body_a,body_b, 
            length=cls.rope_length,
            stiffness=0.0,
            collide_connected=True,
            max_length=cls.rope_length
        )
        graph.add_edge(goo_a, goo_b,joint=j)
        return j


    @classmethod
    def query_placement(self, position):
        pass

    @classmethod
    def draw_goo(cls, position, angle):
        size = (cls.radius*2 * 1.0, cls.radius*2 * 1.1)
        pos = list(position)
        pos[0] -= cls.radius 
        pos[1] -= cls.radius*1.2

        textured_rect(pos, size, cls.texture, angle, rot_origin=list(position))


    @classmethod
    def create(cls, root, position):
        world = root.world

        shape = b2d.circle_shape(radius=cls.radius)
        fixture = b2d.fixture_def(shape=shape, density=1, friction=0.2)
        body = world.create_dynamic_body(
            position=position, 
            fixtures=fixture,
            linear_damping=0.2,
            angular_damping=0.9,
            gravity_scale=-1.0
        )
        goo = cls(root, body)
        root.goo_graph.add_node(goo)
        body.user_data = goo

        return goo



    @classmethod
    def query_placement(cls, root, position, query_only):
        
        def filter_func(bdy):
            goo = bdy.user_data
            if isinstance(goo, GooBase) and \
               goo.can_connect_with_cls(root.goo_cls) and \
               goo.has_free_connection():
               return True
            return False
        bodies = bodies_in_radius(root.world, pos=position, radius=cls.discover_radius,
                                    filter_func=filter_func, max_elements=10)
        goos = [b.user_data for b in bodies]
        n_goos = len(goos)

        print(n_goos)

        if n_goos >= 1:


            # insert as body?
            f = lambda goo :  (goo, (goo.body.position- b2d.vec2(position)).length)

            distances = [f(goo) for goo in goos]
            distances.sort(key=lambda x:x[1])

            best_goo = distances[0][0]
            def draw_callback():
                cls.draw_joint(pos_a=position, pos_b=best_goo.body.position)
                cls.draw_goo(position=position, angle=None)

            def insert_callack():
                goo = cls.create(root=root, position=position)
                root.level.goo_contigent[cls] -= 1
                root.hud.set_amount(cls, root.level.goo_contigent[cls] )
                cls.connect_goos(root, goo, best_goo)

            return True, draw_callback, insert_callack



        return False, None, None





    def __init__(self, root, body):
        super(BaloonGoo, self).__init__(root=root, body=body)
