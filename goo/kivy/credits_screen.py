
from kivy.properties import ObjectProperty
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen



# Create both screens. Please note the root.manager.current: this is how
# you can control the ScreenManager from kv. Each screen has by default a
# property manager that gives you the instance of the ScreenManager used.
Builder.load_string("""
<CreditsScreen>:
    Label:
        text: 'Thorsten Beier'

""")



class CreditsScreen(Screen):
    pass

