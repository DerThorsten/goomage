from b2d.testbed.backend.kivy.kivy_debug_draw import KivyBatchDebugDraw

# kivy
from kivy.uix.widget import Widget
from kivy.graphics.instructions import *
from kivy.graphics.transformation import Matrix
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatter import Scatter, ScatterPlane
from kivy.clock import Clock
from kivy.config import Config


class CanvasWidget(ScatterPlane):
    def __init__(self, **kwargs):

        super(CanvasWidget, self).__init__(**kwargs)
        self.meta_world = None

        scale = 30
        self.apply_transform(Matrix().scale(scale, scale, scale),
                                     anchor=(0,0))

    def install_meta_world(self, meta_world):
        self.meta_world = meta_world
        self.meta_world.canvas = self.canvas

        # clock to trigger stepping of world and rendering
        fps = App.get_running_app().config.get('Goo','fps')
        dt = 1.0 / float(fps)
        Clock.schedule_interval(self.step, dt)

        # apply initial scale
        print(self.scale)

        print(self.scale)

    def step(self, dt):
        self.canvas.clear()
        self.meta_world.step(dt=dt)
        with self.canvas:
            self.meta_world.draw_debug_data()
            self.meta_world.draw()

    def uninstall_meta_world(self):
        self.meta_world = None



    def handle_scroll(self, touch):
        factor = None
        if touch.button == 'scrolldown':
            if self.scale < self.scale_max:
                factor = 1.1
        elif touch.button == 'scrollup':
            if self.scale > self.scale_min:
                factor = 1 / 1.1
        if factor is not None:
            self.apply_transform(Matrix().scale(factor, factor, factor),
                                 anchor=touch.pos)


    def on_touch_down(self, touch):
        # Override Scatter's `on_touch_down` behavior for mouse scroll
        if touch.is_mouse_scrolling:
            self.handle_scroll(touch)
        else:
            world_pos = self.to_local(*touch.pos)
            handled_event =self.meta_world.on_mouse_down(world_pos)
            if not handled_event:
                super(CanvasWidget, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.is_mouse_scrolling:
            pass
        else:
            world_pos = self.to_local(*touch.pos)
            handled_event =self.meta_world.on_mouse_up(world_pos)
            if not handled_event:
                super(CanvasWidget, self).on_touch_up(touch)

    def on_touch_move(self, touch):
        world_pos = self.to_local(*touch.pos)
        handled_event =self.meta_world.on_mouse_move(world_pos)
        if not handled_event:
            super(CanvasWidget, self).on_touch_move(touch)