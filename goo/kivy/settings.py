from kivy.app import App
from kivy.uix.settings import SettingsWithTabbedPanel
from kivy.logger import Logger


# This JSON defines entries we want to appear in our App configuration screen
json_settings = '''
[
    {
        "type": "string",
        "title": "Label caption",
        "desc": "Choose the text that appears in the label",
        "section": "Goo",
        "key": "text"
    },
    {
        "type": "numeric",
        "title": "Label font size",
        "desc": "Choose the font size the label",
        "section": "Goo",
        "key": "font_size"
    },
    {
        "type": "numeric",
        "title": "fps",
        "desc": "fps",
        "section": "Goo",
        "key": "fps"
    },
    {
        "type": "bool",
        "title": "sound",
        "desc": "sound",
        "section": "Goo",
        "key": "sound"
    },
    {
        "type": "bool",
        "title": "draw_debug_data",
        "desc": "draw_debug_data",
        "section": "Goo",
        "key": "draw_debug_data"
    }
]
'''

class MySettingsWithTabbedPanel(SettingsWithTabbedPanel):
    """
    It is not usually necessary to create subclass of a settings panel. There
    are many built-in types that you can use out of the box
    (SettingsWithSidebar, SettingsWithSpinner etc.).
    You would only want to create a Settings subclass like this if you want to
    change the behavior or appearance of an existing Settings class.
    """
    def on_close(self):
        Logger.info("main.py: MySettingsWithTabbedPanel.on_close")

    def on_config_change(self, config, section, key, value):
        Logger.info(
            "main.py: MySettingsWithTabbedPanel.on_config_change: "
            "{0}, {1}, {2}, {3}".format(config, section, key, value))

