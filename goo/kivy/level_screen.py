from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import *
from . canvas import CanvasWidget
from . meta_world import MetaWorld



Builder.load_string("""
<GooHUDEntry>:
    orientation: 'vertical'
    MyButton:
        canvas:
            Color:
                rgba: (1, 1, 1, 0.1) if  root.is_selected  else (1, 1, 1, 0.0)
            Rectangle:
                pos: self.pos
                size: self.width  , self.height 
        source: root.source
        on_release : root.on_release()
    Label:
        size_hint_y: 0.2
        text: str(root.amount)

<HUD>:
    canvas:
        Color:
            rgba: 0.1, 0.1, 0.1, 1
        Rectangle:
            pos: self.pos
            size: self.width  , self.height + 10

    orientation: 'horizontal'

<LevelScreen>:
    canvas_widget: canvas_widget
    hud: hud
    BoxLayout:
        orientation: 'vertical'
        CanvasWidget:
            id: canvas_widget
            hud: hud
            do_rotation: 0
        HUD:
            id: hud
            size_hint_y: 0.1
            size_hint_x: 1
        
""")
class MyButton(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super(MyButton, self).__init__(**kwargs)
        # self.source = 


class GooHUDEntry(BoxLayout):
    goo_cls = ObjectProperty(None)
    hud = ObjectProperty(None)
    source  = StringProperty("")
    is_selected = BooleanProperty(False)
    amount = NumericProperty(0)

    def on_release(self):
        self.is_selected = True
        self.hud.on_goo_button_released(self)

class HUD(BoxLayout):


    def install_meta_world(self, meta_world):
        self.meta_world = meta_world
        self.meta_world.hud = self

        self.goo_contigent = self.meta_world.level.goo_contigent
        first = True
        self.hud_entries = {}
        for goo_cls, amount in self.goo_contigent.items():
            hud_entry = GooHUDEntry()
            hud_entry.goo_cls = goo_cls
            hud_entry.source = goo_cls.texture_path
            hud_entry.hud = self
            hud_entry.amount = amount
            if first:
                hud_entry.is_selected = True
                first = False
            self.add_widget(hud_entry)
            self.hud_entries[goo_cls] = hud_entry

    def on_goo_button_released(self, releasing):
        self.meta_world.goo_cls = releasing.goo_cls
        for goo_cls, hud_entry in self.hud_entries.items():
            if hud_entry != releasing:
                hud_entry.is_selected = False



    def set_amount(self, cls, amount):
        self.hud_entries[cls].amount = amount
    

class LevelScreen(Screen):
    
    def on_pre_enter(self):
        print("pre-enter")

    def on_enter(self):
        app = App.get_running_app()
        meta_world = MetaWorld(level_cls=app.current_level)

        self.canvas_widget.install_meta_world(meta_world)
        self.hud.install_meta_world(meta_world)

