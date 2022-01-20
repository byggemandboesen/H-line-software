from kivy.config import Config
Config.set('graphics', 'resizable', 0)

from kivy.lang.builder import Builder
from kivy.core.window import Window
from kivymd.app import MDApp

class PyLineSDR(MDApp):
    def build(self):
        Window.size = (1000, 500)
        return Builder.load_file("src/ui.kv")

if __name__ == "__main__":
    PyLineSDR().run()
