from kivy.logger import Logger

import networkx
import b2d
from b2d.testbed.backend.kivy.kivy_debug_draw import KivyBatchDebugDraw

from ..goos import *
from ..items import *
from .textures import images, sounds

from kivy.core.image import Image
from kivy.graphics import *





class MetaWorld(
    b2d.DestructionListener,
    b2d.ContactListener
):
    def __init__(self, level_cls):

        b2d.ContactListener.__init__(self)
        b2d.DestructionListener.__init__(self)


        self.world = b2d.world(gravity=(0,-10))
        self.debug_draw = KivyBatchDebugDraw()
        self.world.set_debug_draw(self.debug_draw)
        self.goo_graph = networkx.Graph()
        Logger.info("construct level")
        self.level = level_cls(root=self)
        Logger.info("construct level done")


        # listeners
        self.world.set_contact_listener(self)
        self.world.set_destruction_listener(self)

        # mouse related
        self._mouse_is_down = False
        self._last_pos = None
        self._handled_click = False
    

        # the current goo to place
        self.goo_cls = PlainGoo
        self._insert_info = InsertInfo(InsertType.CANNOT_INSERT)

        # goo-s do be destroyed in the next step
        self.marked_for_destruction = []


    def on_mouse_down(self, pos):
        Logger.debug("on_mouse_down", pos)
        self._mouse_is_down = True
        self._last_pos = pos
        self._insert_info = query_goo_placement(self, pos)
        handled = False
        if self._insert_info.insert_type == InsertType.CANNOT_INSERT:
            self._handled_click = False
            return False# super(MetaWorld, self).on_mouse_down(pos)
        else:
            self._handled_click = True
            return True


    def on_mouse_move(self, pos):
        Logger.debug("on_mouse_move", pos)
        handled = False
        self._last_pos = pos
        if self._mouse_is_down:
           self._insert_info = query_goo_placement(self, pos)
        handled = False
        if not self._handled_click:
            return False #super(MetaWorld, self).on_mouse_move(pos)
        else:
            return True

    def on_mouse_up(self, pos):
        Logger.debug("on_mouse_up", pos)
        self._mouse_is_down = False
        self._insert_info = query_goo_placement(self, pos)
        if self._insert_info.insert_type == InsertType.AS_GOO:

            goo = self.goo_cls.create(self, position=pos)
            goo_a = self._insert_info.info['goo_a']
            goo_b = self._insert_info.info['goo_b']
            # connect_goo_tripple(self, goo_a, goo_b, goo_new=goo)
            connect_goos(self, goo, goo_a)
            connect_goos(self, goo, goo_b)

            if sounds['blub']!= 'stop':
                sounds['blub'].stop()
            sounds['blub'].seek(0)
            sounds['blub'].play()
            sounds['blub'].loop = False
            # sounds['blub'].stop()
        elif self._insert_info.insert_type == InsertType.AS_JOINT:
            goo_a = self._insert_info.info['goo_a']
            goo_b = self._insert_info.info['goo_b']
            connect_goos(self, goo_b, goo_a)
            sounds['blub'].play()
            sounds['blub'].loop = False
            # sounds['blub'].stop()
        self._insert_info = InsertType.CANNOT_INSERT
        self._last_pos = pos
        handled = False
        if not self._handled_click:
            return False #super(MetaWorld, self).on_mouse_up(pos)
        else:
            self._handled_click = False
            return True


    def pre_debug_draw(self):
        pass


    def post_debug_draw(self):
        
        if self._mouse_is_down and  self._last_pos is not None:

            self.goo_cls.draw_tentative(self, self._last_pos, 
                insert_info=self._insert_info)

    def draw_debug_data(self):

        callback = b2d.testbed.testbed_base.DebugDrawCallback(
            pre_debug_draw=self.pre_debug_draw,
            post_debug_draw=self.post_debug_draw
        )
        # self.world.draw_debug_data(callback)


    def draw(self):
   
        if self._mouse_is_down and  self._last_pos is not None:

            self.goo_cls.kivy_draw_tentative(self, self._last_pos, 
                insert_info=self._insert_info)


        for (goo_a, goo_b, joint) in self.goo_graph.edges(data='joint'):
            anchor_a = tuple(joint.anchor_a)
            anchor_b = tuple(joint.anchor_b)
            Line(points=[anchor_a, anchor_b], width=0.15, color=Color(0.5,0.5,1,1))

        for goo in self.goo_graph:
            
            radius = goo.radius
            size = (radius*2, radius*2)
            pos = list(goo.body.position)
            pos[0] -= radius
            pos[1] -= radius
            Color(1,1,1,1)
            Rectangle(size=size, pos=pos,texture=images['plain_goo'].texture)

        self.level.kivy_draw()

 
    def pre_step(self, dt):
        for goo in self.marked_for_destruction:
            self.goo_graph.remove_node(goo)
            self.world.destroy_body(goo.body)
        self.marked_for_destruction = []


    def post_step(self, dt):
        pass

    def step(self, dt):
        self.pre_step(dt)
        self.world.step(dt, 2,2)
        self.post_step(dt)


    def begin_contact(self, contact):
        user_data_a = contact.body_a.user_data
        user_data_b = contact.body_b.user_data
        a_is_goo =  isinstance(user_data_a, GooBase)
        b_is_goo =  isinstance(user_data_b, GooBase)

        if xor(a_is_goo, b_is_goo):
            if a_is_goo:
                self.begin_goo_contact(user_data_a, user_data_b)
            else:
                self.begin_goo_contact(user_data_b, user_data_a)



    def begin_goo_contact(self, goo, other):
        if isinstance(other, Destroyer):
            self.marked_for_destruction.append(goo)
