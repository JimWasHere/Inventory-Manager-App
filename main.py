from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
import json
import os

from shelf_manager.shelf_management import ShelfManagementScreen  # Ensure folder structure is correct


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Paths for JSON file and backup
        self.json_file_path = "assets/inventory.json"
        self.backup_file_path = "assets/inventory_backup.json"

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Buttons for accessing Shelf Management and Search Apps
        layout.add_widget(Button(text="Open Shelf Management App", on_press=self.open_shelf_management))
        layout.add_widget(Button(text="Open Search App", on_press=self.open_search_app))

        # JSON file handling options
        layout.add_widget(Button(text="Load/Create JSON File", on_press=self.load_json_file))
        layout.add_widget(Button(text="Backup/Reset JSON File", on_press=self.backup_reset_json_file))

        # Status indicator
        self.status_label = Label(text="Status: JSON file not loaded")
        layout.add_widget(self.status_label)

        self.add_widget(layout)

    def open_shelf_management(self, instance):
        self.manager.current = 'shelf_management'

    def open_search_app(self, instance):
        # Placeholder for actual screen switch or app launch logic
        self.status_label.text = "Search App opened."

    def load_json_file(self, instance):
        if not os.path.exists(self.json_file_path):
            # Create a new JSON file with an empty structure
            initial_data = {"locations": {}}
            with open(self.json_file_path, 'w') as json_file:
                json.dump(initial_data, json_file, indent=4)
            self.status_label.text = "New JSON file created."
        else:
            # Load existing JSON file
            with open(self.json_file_path, 'r') as json_file:
                data = json.load(json_file)
            self.status_label.text = "JSON file loaded successfully."

    def backup_reset_json_file(self, instance):
        # Backup current JSON file
        if os.path.exists(self.json_file_path):
            with open(self.json_file_path, 'r') as original_file:
                data = original_file.read()
            with open(self.backup_file_path, 'w') as backup_file:
                backup_file.write(data)
            self.status_label.text = "JSON file backed up successfully."
        else:
            self.status_label.text = "No JSON file to back up."

        # Reset the JSON file to initial structure
        initial_data = {"locations": {}}
        with open(self.json_file_path, 'w') as json_file:
            json.dump(initial_data, json_file, indent=4)
        self.status_label.text = "JSON file reset to initial structure."


class MainApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(ShelfManagementScreen(name='shelf_management', json_file_path="assets/inventory.json"))
        return sm


if __name__ == '__main__':
    MainApp().run()
