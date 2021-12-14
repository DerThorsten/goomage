
from kivy.properties import ObjectProperty
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen



# Create both screens. Please note the root.manager.current: this is how
# you can control the ScreenManager from kv. Each screen has by default a
# property manager that gives you the instance of the ScreenManager used.
Builder.load_string("""
<MenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        Button:
            text: 'Level 1'
            on_press: root.manager.current = 'level'

        Button:
            text: 'Settings'
            on_press: app.open_settings()

        Button:
            text: 'Credits'
            on_press: root.manager.current = 'credits'

""")



class MenuScreen(Screen):
    pass

