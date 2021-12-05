
from kivy.properties import ObjectProperty
from kivy.config import ConfigParser
from kivy.logger import Logger

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

from . canvas import CanvasWidget
from . meta_world import MetaWorld
from . settings import json_settings, MySettingsWithTabbedPanel
from ..level import Level1


# Create both screens. Please note the root.manager.current: this is how
# you can control the ScreenManager from kv. Each screen has by default a
# property manager that gives you the instance of the ScreenManager used.
Builder.load_string("""
<MenuScreen>:
    BoxLayout:
        Button:
            text: 'Level 1'
            on_press: root.manager.current = 'level'

        Button:
            text: 'Settings'
            on_press: app.open_settings()

<LevelScreen>:
    canvas_widget: canvas_widget
    button_widget: button_widget
    FloatLayout:
        CanvasWidget:
            id: canvas_widget
            button_widget: button_widget
            do_rotation: 0
        Button:
            id: button_widget
            size_hint:(.5, .25)
            pos:(20, 20)
            on_release: print("acc")


""")



class MenuScreen(Screen):
    pass

class LevelScreen(Screen):
    
    def on_pre_enter(self):
        print("pre-enter")

    def on_enter(self):
        app = App.get_running_app()
        meta_world = MetaWorld(level_cls=app.current_level)
        self.canvas_widget.install_meta_world(meta_world)
        

class GooApp(App):
    def __init__(self):
        self.current_level = Level1
        super(GooApp, self).__init__()

    def build(self):


        self.settings_cls = MySettingsWithTabbedPanel

        # Create the screen manager
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(LevelScreen(name='level'))
        return sm

    def build_config(self, config):
        """
        Set the default values for the configs sections.
        """
        config.setdefaults('Goo', 
            {
                'text': 'Hello', 
                'font_size': 20,
                'fps' : 40
            })

    def build_settings(self, settings):
        """
        Add our custom section to the default configuration object.
        """
        # We use the string defined above for our JSON, but it could also be
        # loaded from a file as follows:
        #     settings.add_json_panel('Goo', self.config, 'settings.json')
        settings.add_json_panel('Goo', self.config, data=json_settings)

    def on_config_change(self, config, section, key, value):
        """
        Respond to changes in the configuration.
        """
        Logger.info("main.py: App.on_config_change: {0}, {1}, {2}, {3}".format(
            config, section, key, value))

        # if section == "Goo":
        #     if key == "text":
        #         self.root.ids.label.text = value
        #     elif key == 'font_size':
        #         self.root.ids.label.font_size = float(value)

    def close_settings(self, settings=None):
        """
        The settings panel has been closed.
        """
        Logger.info("main.py: App.close_settings: {0}".format(settings))
        super(GooApp, self).close_settings(settings)


