from kivy.logger import Logger

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from . level_screen import LevelScreen
from . menu_screen import MenuScreen
from . credits_screen import CreditsScreen
from . settings import json_settings, MySettingsWithTabbedPanel
from ..level import Level1


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
        sm.add_widget(CreditsScreen(name='credits'))
        return sm

    def build_config(self, config):
        """
        Set the default values for the configs sections.
        """
        config.setdefaults('Goo', 
            {
                'text': 'Hello', 
                'font_size': 20,
                'fps' : 40,
                'sound':True,
                'draw_debug_data':False
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


