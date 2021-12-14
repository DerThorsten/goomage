from kivy.logger import Logger

import networkx
import b2d
from .debug_draw import KivyBatchDebugDraw
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
        self.goo_cls = self.level.selected_goo
        self._insert_info = InsertInfo(InsertType.CANNOT_INSERT)

        # goo-s do be destroyed in the next step
        self.marked_for_destruction = []

        self._goo_placement_info_draw_callback = None


    def query_placement(self, position, query_only):
        Logger.info(f"query_placement {position=} {query_only=}")

        if self.level.goo_contigent[self.goo_cls] <= 0:
            can_be_placed, draw_callback, insert_callback,  = False, None, None
        else:
            can_be_placed, draw_callback, insert_callback = self.goo_cls.query_placement(root=self, position=position, query_only=query_only)
        
        if can_be_placed:
            self._goo_placement_info_draw_callback = draw_callback
        else:
            self._goo_placement_info_draw_callback = None

        return can_be_placed, draw_callback, insert_callback

    def on_mouse_down(self, pos):
        Logger.debug("on_mouse_down", pos)
        self._mouse_is_down = True

        can_be_placed,_,_ = self.query_placement(position=pos, query_only=True)
        return can_be_placed

        # handled = False
        # if self._insert_info.insert_type == InsertType.CANNOT_INSERT:
        #     self._handled_click = False
        #     return False# super(MetaWorld, self).on_mouse_down(pos)
        # else:
        #     self._handled_click = True
        #     return True


    def on_mouse_move(self, pos):
        Logger.debug("on_mouse_move", pos)

        can_be_placed,_,_ = self.query_placement(position=pos, query_only=True)
        return can_be_placed


        # handled = False
        # self._last_pos = pos
        # if self._mouse_is_down:
        #    pass
        # handled = False
        # if not self._handled_click:
        #     return False #super(MetaWorld, self).on_mouse_move(pos)
        # else:
        #     return True

    def on_mouse_up(self, pos):
        # print(self.level.goo_contigent)
        Logger.debug("on_mouse_up", pos)

        can_be_placed,_,insert_callback = self.query_placement(position=pos, query_only=False)
        if can_be_placed:
            insert_callback()
        self._mouse_is_down = False
        self._goo_placement_info_draw_callback = None
        pass


        # if self._insert_info.insert_type == InsertType.AS_GOO:

        #     self.level.goo_contigent[self.goo_cls] -= 1
        #     self.hud.set_amount(self.goo_cls, self.level.goo_contigent[self.goo_cls] )

        #     goo = self.goo_cls.create(self, position=pos)
        #     goo_a = self._insert_info.info['goos'][0]
        #     goo_b = self._insert_info.info['goos'][1]
        #     # connect_goo_tripple(self, goo_a, goo_b, goo_new=goo)
        #     connect_goos(self, goo, goo_a)
        #     connect_goos(self, goo, goo_b)

        #     if sounds['blub']!= 'stop':
        #         sounds['blub'].stop()
        #     sounds['blub'].seek(0)
        #     sounds['blub'].play()
        #     sounds['blub'].loop = False
        #     # sounds['blub'].stop()
        # elif self._insert_info.insert_type == InsertType.AS_JOINT:

        #     self.level.goo_contigent[self.goo_cls] -= 1
        #     self.hud.set_amount(self.goo_cls, self.level.goo_contigent[self.goo_cls] )

        #     goo_a = self._insert_info.info['goos'][0]
        #     goo_b = self._insert_info.info['goos'][1]
        #     connect_goos(self, goo_b, goo_a)
        #     sounds['blub'].play()
        #     sounds['blub'].loop = False
        #     # sounds['blub'].stop()
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
        pass        
        # if self._mouse_is_down and  self._last_pos is not None:

        #     self.goo_cls.debug_draw_tentative(self, self._last_pos, 
        #         insert_info=self._insert_info)

    def draw_debug_data(self):

        callback = b2d.testbed.testbed_base.DebugDrawCallback(
            pre_debug_draw=self.pre_debug_draw,
            post_debug_draw=self.post_debug_draw
        )
        self.world.draw_debug_data(callback)


    def draw(self):

        # this will to things like tentative drawing
        if self._goo_placement_info_draw_callback is not None:
            self._goo_placement_info_draw_callback()

   
        # if self._mouse_is_down and  self._last_pos is not None:

        #     self.goo_cls.kivy_draw_tentative(self, self._last_pos, 
        #         insert_info=self._insert_info)


        for (goo_a, goo_b, joint) in self.goo_graph.edges(data='joint'):
            anchor_a = tuple(joint.anchor_a)
            anchor_b = tuple(joint.anchor_b)
            Line(points=[anchor_a, anchor_b], width=0.15, color=Color(0.5,0.5,1,1))

        for goo in self.goo_graph:
            goo.draw()


        self.level.kivy_draw()



 
    def pre_step(self, dt):

        # destroy goos
        for goo in self.marked_for_destruction:
            self.goo_graph.remove_node(goo)
            self.world.destroy_body(goo.body)
        self.marked_for_destruction = []


        # clear all buffs
        for goo in self.goo_graph:
            goo.remove_buffs()

        # pre-step each goo
        for pass_nr in range(0,1):
            for goo in self.goo_graph.nodes():
                goo.pre_step(dt, pass_nr=pass_nr)

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
