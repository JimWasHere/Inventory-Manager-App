from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
import json
import os


class ShelfManagementScreen(Screen):
    def __init__(self, json_file_path, **kwargs):
        super().__init__(**kwargs)
        self.json_file_path = json_file_path

        # Layout for Shelf Management screen
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Button to display current locations
        layout.add_widget(Button(text="Display Locations", on_press=self.display_locations))

        # Buttons to add/remove locations and shelves
        layout.add_widget(Button(text="Add New Location", on_press=self.add_location_popup))
        layout.add_widget(Button(text="Remove Location", on_press=self.remove_location_popup))

        # Status indicator
        self.status_label = Label(text="Status: Ready")
        layout.add_widget(self.status_label)

        self.add_widget(layout)

    def load_json_data(self):
        """Utility function to load JSON data."""
        if os.path.exists(self.json_file_path):
            with open(self.json_file_path, 'r') as file:
                return json.load(file)
        return {"locations": {}}

    def save_json_data(self, data):
        """Utility function to save JSON data."""
        with open(self.json_file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def display_locations(self, instance):
        """Display current locations with an option to add shelves in a popup."""
        data = self.load_json_data()
        locations = data.get("locations", {})
        location_list = "\n".join(locations.keys()) if locations else "No locations available."

        # Create layout for displaying locations
        popup_content = BoxLayout(orientation='vertical', spacing=10)

        # If locations exist, show each location with an "Add Shelf" button
        if locations:
            for location_name in locations.keys():
                location_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=44)
                location_label = Label(text=location_name, size_hint_x=0.7)
                add_shelf_button = Button(text="Add Shelf", size_hint_x=0.3)

                # Bind the "Add Shelf" button to open the add_shelf_popup for this location
                add_shelf_button.bind(on_press=lambda btn, loc=location_name: self.add_shelf_popup(loc))

                location_box.add_widget(location_label)
                location_box.add_widget(add_shelf_button)
                popup_content.add_widget(location_box)
        else:
            popup_content.add_widget(Label(text="No locations available."))

        # Add close button
        close_button = Button(text="Close", size_hint=(1, 0.2))
        popup_content.add_widget(close_button)

        # Display the popup
        popup = Popup(title="Current Locations", content=popup_content, size_hint=(0.8, 0.8))
        close_button.bind(on_press=popup.dismiss)
        popup.open()

    def add_location_popup(self, instance):
        """Popup to add a new location."""
        popup_content = BoxLayout(orientation='vertical')

        # Text input for the location name
        location_input = TextInput(hint_text="Enter location name")
        popup_content.add_widget(location_input)

        # Button to confirm adding the location
        add_button = Button(text="Add Location", size_hint=(1, 0.2))
        popup_content.add_widget(add_button)

        popup = Popup(title="Add New Location", content=popup_content, size_hint=(0.8, 0.4))

        # Bind the add_button to the method that will handle adding the location
        add_button.bind(on_press=lambda x: self.add_location(location_input.text, popup))
        popup.open()

    def add_location(self, location_name, popup):
        """Add a new location to the JSON structure."""
        # Load existing data
        data = self.load_json_data()

        # Check if the location already exists
        if location_name in data["locations"]:
            self.status_label.text = f"Location '{location_name}' already exists."
        else:
            # Add the new location with an empty dictionary for shelves
            data["locations"][location_name] = {}
            self.save_json_data(data)
            self.status_label.text = f"Location '{location_name}' added successfully."

        # Close the popup after adding the location
        popup.dismiss()

    def remove_location_popup(self, instance):
        """Popup to select a location to remove."""
        data = self.load_json_data()
        locations = data.get("locations", {})

        # Check if there are locations available
        if not locations:
            self.status_label.text = "No locations available to remove."
            return

        # Create layout for displaying locations with remove option
        popup_content = BoxLayout(orientation='vertical', spacing=10)
        for location_name in locations.keys():
            location_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=44)
            location_label = Label(text=location_name, size_hint_x=0.7)
            remove_button = Button(text="Remove", size_hint_x=0.3)

            # Bind the remove button to confirm removal
            remove_button.bind(on_press=lambda btn, loc=location_name: self.confirm_remove_location(loc, popup))

            location_box.add_widget(location_label)
            location_box.add_widget(remove_button)
            popup_content.add_widget(location_box)

        # Add close button
        close_button = Button(text="Close", size_hint=(1, 0.2))
        popup_content.add_widget(close_button)

        # Display the popup
        popup = Popup(title="Remove Location", content=popup_content, size_hint=(0.8, 0.8))
        close_button.bind(on_press=popup.dismiss)
        popup.open()

    def confirm_remove_location(self, location_name, parent_popup):
        """Ask the user to confirm removal of the location."""
        popup_content = BoxLayout(orientation='vertical', spacing=10)
        popup_content.add_widget(
            Label(text=f"Are you sure you want to delete '{location_name}'? This action cannot be undone."))

        # Yes button to confirm deletion
        yes_button = Button(text="Yes", size_hint=(1, 0.2))

        # Create the confirmation popup and pass it to remove_location for dismissal
        confirmation_popup = Popup(title="Confirm Deletion", content=popup_content, size_hint=(0.8, 0.4))
        yes_button.bind(on_press=lambda x: self.remove_location(location_name, parent_popup, confirmation_popup))

        # No button to cancel
        no_button = Button(text="No", size_hint=(1, 0.2))
        no_button.bind(on_press=confirmation_popup.dismiss)

        popup_content.add_widget(yes_button)
        popup_content.add_widget(no_button)

        # Display confirmation popup
        confirmation_popup.open()

    def remove_location(self, location_name, parent_popup, confirmation_popup):
        """Remove the specified location from the JSON structure."""
        data = self.load_json_data()

        # Check if the location exists and remove it
        if location_name in data["locations"]:
            del data["locations"][location_name]
            self.save_json_data(data)
            self.status_label.text = f"Location '{location_name}' removed successfully."
        else:
            self.status_label.text = f"Location '{location_name}' does not exist."

        # Close both the original location popup and the confirmation popup
        parent_popup.dismiss()
        confirmation_popup.dismiss()

    def select_location_for_shelf_popup(self, instance):
        """Popup to select a location to add a new shelf."""
        data = self.load_json_data()
        locations = data.get("locations", {})

        # Check if there are locations available
        if not locations:
            self.status_label.text = "No locations available. Please add a location first."
            return

        # Create a popup with a list of location buttons
        popup_content = BoxLayout(orientation='vertical', spacing=10)
        for location_name in locations.keys():
            btn = Button(text=location_name, size_hint_y=None, height=44)
            btn.bind(
                on_press=lambda btn: self.add_shelf_popup(btn.text))  # Opens add_shelf_popup with the selected location
            popup_content.add_widget(btn)

        # Add a close button
        close_button = Button(text="Close", size_hint=(1, 0.2))
        popup_content.add_widget(close_button)

        # Display the popup
        popup = Popup(title="Select Location", content=popup_content, size_hint=(0.8, 0.8))
        close_button.bind(on_press=popup.dismiss)
        popup.open()

    def add_shelf_popup(self, location_name):
        """Popup to add a new shelf to a selected location."""
        popup_content = BoxLayout(orientation='vertical')

        # Text input for the shelf name
        shelf_input = TextInput(hint_text="Enter shelf name")
        popup_content.add_widget(shelf_input)

        # Button to confirm adding the shelf
        add_button = Button(text="Add Shelf", size_hint=(1, 0.2))
        popup_content.add_widget(add_button)

        popup = Popup(title=f"Add New Shelf to {location_name}", content=popup_content, size_hint=(0.8, 0.4))

        # Bind the add_button to the method that will handle adding the shelf
        add_button.bind(on_press=lambda x: self.add_shelf(location_name, shelf_input.text, popup))
        popup.open()

    def add_shelf(self, location_name, shelf_name, popup):
        """Add a new shelf to the specified location in the JSON structure."""
        # Load existing data
        data = self.load_json_data()

        # Check if the location exists
        if location_name not in data["locations"]:
            self.status_label.text = f"Location '{location_name}' does not exist."
        elif shelf_name in data["locations"][location_name]:
            self.status_label.text = f"Shelf '{shelf_name}' already exists in '{location_name}'."
        else:
            # Add the new shelf with an empty dictionary for nested shelves
            data["locations"][location_name][shelf_name] = {}
            self.save_json_data(data)
            self.status_label.text = f"Shelf '{shelf_name}' added to '{location_name}' successfully."

        # Close the popup after adding the shelf
        popup.dismiss()
