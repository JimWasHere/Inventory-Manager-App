from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen

class MainScreen(Screen):
    pass

class MainApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        # Add other screens here as needed later
        return sm

if __name__ == '__main__':
    MainApp().run()
