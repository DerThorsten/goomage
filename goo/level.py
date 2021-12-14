import random
import numpy
import b2d 
import collections

from .items import Destroyer, Goal
from .goos  import *

class LevelBase(object):

    def __init__(self):

        self.goo_contigent = collections.OrderedDict()

    @property
    def end_sensor(self):
        raise NotImplementedError


    @property
    def kill_sensors(self):
        raise NotImplementedError

    def draw(self):
        raise NotImplementedError

    def n_goos(self, goo_cls):
        assert goo_cls in self.goo_contigent
        return self.goo_contigent[goo_cls]



class Level1(LevelBase):
    
    def kivy_draw(self):

        for w,a in [(1.0,1.0), (1.5, 0.5), (3, 0.2), (6, 0.1)]:
            Line(points=self.outline_verts, 
                width=0.15*w, color=Color(0.5,0.5,1,a))




    def __init__(self, root):
        super(Level1, self).__init__()
        self.root = root
        self.world = self.root.world

        self.goo_contigent[PlainGoo] = 30
        self.goo_contigent[AnchorGoo] = 30
        self.goo_contigent[BaloonGoo] = 30
        self.goo_contigent[MagicGoo] = 30
        self.selected_goo = PlainGoo

        kill_sensors_height=0.5
        gap_size = 30
        usable_size = 20
        h = 10
        end_zone_height = 3
        
        self.outline_verts = [
            (0,2*h),
            (0,h),
            (usable_size,h),
            (usable_size,0),
            (usable_size+gap_size,0),
            (usable_size+gap_size,h),
            (2*usable_size+gap_size,h),
            (2*usable_size+gap_size,2*h)
        ]

        # outline of the level
        shape =  b2d.chain_shape(
            vertices=numpy.flip(self.outline_verts,axis=0)
        )
        self.outline = self.world.create_static_body( position=(0, 0), shape = shape)

        # kill sensors
        shape =b2d.polygon_shape(box=(gap_size/2,kill_sensors_height/2))
        self._kill_sensor = self.world.create_static_body(
            position=(usable_size+gap_size/2, kill_sensors_height/2),
            fixtures=b2d.fixture_def(
                shape=shape,
                is_sensor=True
            ),
        )
        self._kill_sensor.user_data = Destroyer(body=self._kill_sensor)


        # end sensor
        shape =b2d.polygon_shape(box=(usable_size/2,end_zone_height/2))
        self._end_sensor = self.world.create_static_body(
            position=(1.5*usable_size+gap_size, h+end_zone_height/2),
            fixtures=b2d.fixture_def(
                shape=shape,
                is_sensor=True
            ),
        )
        self._end_sensor.user_data = Goal(body=self._end_sensor)

        # place goos
        a = AnchorGoo.create(self.root, position=(usable_size/3,h + AnchorGoo.radius))
        b = AnchorGoo.create(self.root, position=(usable_size*2/3,h + AnchorGoo.radius))
        c = AnchorGoo.create(self.root, position=(usable_size*1/2,h + AnchorGoo.radius + 3))

        # d = BaloonGoo.create(self.root, position=(usable_size*1/2,h + AnchorGoo.radius + 8))

        j = AnchorGoo.connect_goos(self.root, a,b)
        j = AnchorGoo.connect_goos(self.root, a,c)
        j = AnchorGoo.connect_goos(self.root, b,c)

        # j = BaloonGoo.connect_goos(self.root, c,d)