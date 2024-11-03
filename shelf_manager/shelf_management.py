from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from camera_scanner import CameraScanner
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
        """Display current locations with an option to view shelves."""
        data = self.load_json_data()
        locations = data.get("locations", {})

        # Create layout for displaying locations
        popup_content = BoxLayout(orientation='vertical', spacing=10)

        if locations:
            for location_name in locations.keys():
                location_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=44)
                location_label = Label(text=location_name, size_hint_x=0.7)
                view_shelves_button = Button(text="View Shelves", size_hint_x=0.3)

                # Bind the "View Shelves" button to open the shelves of this location
                view_shelves_button.bind(on_press=lambda btn, loc=location_name: self.view_shelves_popup(loc))

                location_box.add_widget(location_label)
                location_box.add_widget(view_shelves_button)
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

    def view_shelves_popup(self, location_name):
        """Popup to view shelves in the selected location."""
        data = self.load_json_data()
        shelves = data["locations"].get(location_name, {})

        # Create layout for displaying shelves
        popup_content = BoxLayout(orientation='vertical', spacing=10)


        if shelves:
            for shelf_name in shelves.keys():
                shelf_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=44)
                shelf_label = Label(text=shelf_name, size_hint_x=0.7)
                view_nested_shelves_button = Button(text="View Nested Shelves", size_hint_x=0.3)
                remove_shelf_button = Button(text="Remove Shelf", size_hint_x=0.3)
                remove_shelf_button.bind(
                    on_press=lambda btn, sh=shelf_name: self.remove_shelf(location_name, sh, popup))

                # Bind the button to view nested shelves in this shelf
                view_nested_shelves_button.bind(
                    on_press=lambda btn, sh=shelf_name: self.view_nested_shelves_popup(location_name, sh))

                shelf_box.add_widget(shelf_label)
                shelf_box.add_widget(view_nested_shelves_button)
                popup_content.add_widget(shelf_box)
        else:
            popup_content.add_widget(Label(text=f"No shelves available in '{location_name}'."))

        # Add "Add Shelf" button and close button
        add_shelf_button = Button(text="Add New Shelf", size_hint=(1, 0.2))
        add_shelf_button.bind(on_press=lambda x: self.add_shelf_popup(location_name))
        popup_content.add_widget(add_shelf_button)

        close_button = Button(text="Close", size_hint=(1, 0.2))
        popup_content.add_widget(close_button)

        # Display the popup
        popup = Popup(title=f"Shelves in {location_name}", content=popup_content, size_hint=(0.8, 0.8))
        close_button.bind(on_press=popup.dismiss)
        popup.open()

    def add_location_popup(self, instance):
        """Popup to add a new location."""
        popup_content = BoxLayout(orientation='vertical')

        # Text input for the location name
        location_input = TextInput(hint_text="Enter location name", focus=True)
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
        shelf_input = TextInput(hint_text="Enter shelf name", focus=True)
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
        data = self.load_json_data()

        # Check if the shelf already exists
        if shelf_name in data["locations"][location_name]:
            self.status_label.text = f"Shelf '{shelf_name}' already exists in '{location_name}'."
        else:
            # Add the new shelf with an empty dictionary for nested shelves
            data["locations"][location_name][shelf_name] = {}
            self.save_json_data(data)
            self.status_label.text = f"Shelf '{shelf_name}' added to '{location_name}' successfully."

        # Refresh by closing and reopening the shelves popup
        popup.dismiss()
        self.view_shelves_popup(location_name)

    def remove_shelf(self, location_name, shelf_name, popup):
        """Remove the specified shelf from the JSON structure."""
        data = self.load_json_data()
        if shelf_name in data["locations"][location_name]:
            del data["locations"][location_name][shelf_name]
            self.save_json_data(data)
            self.status_label.text = f"Shelf '{shelf_name}' removed from '{location_name}' successfully."

        # Refresh the shelves popup
        popup.dismiss()
        self.view_shelves_popup(location_name)

    def select_shelf_for_nested_shelf_popup(self, location_name):
        """Popup to select a shelf to add a nested shelf."""
        data = self.load_json_data()
        shelves = data["locations"].get(location_name, {})

        # Check if there are shelves available
        if not shelves:
            self.status_label.text = f"No shelves available in '{location_name}'. Please add a shelf first."
            return

        # Create a popup with a list of shelves
        popup_content = BoxLayout(orientation='vertical', spacing=10)
        for shelf_name in shelves.keys():
            btn = Button(text=shelf_name, size_hint_y=None, height=44)
            btn.bind(on_press=lambda btn: self.add_nested_shelf_popup(location_name, btn.text))
            popup_content.add_widget(btn)

        # Add close button
        close_button = Button(text="Close", size_hint=(1, 0.2))
        popup_content.add_widget(close_button)

        # Display the popup
        popup = Popup(title="Select Shelf", content=popup_content, size_hint=(0.8, 0.8))
        close_button.bind(on_press=popup.dismiss)
        popup.open()

    def add_nested_shelf_popup(self, location_name, shelf_name):
        """Popup to add a new nested shelf to a selected shelf."""
        popup_content = BoxLayout(orientation='vertical')

        # Text input for the nested shelf name
        nested_shelf_input = TextInput(hint_text="Enter nested shelf name", focus=True)
        popup_content.add_widget(nested_shelf_input)

        # Button to confirm adding the nested shelf
        add_button = Button(text="Add Nested Shelf", size_hint=(1, 0.2))
        popup_content.add_widget(add_button)

        popup = Popup(title=f"Add Nested Shelf to {shelf_name}", content=popup_content, size_hint=(0.8, 0.4))

        # Bind the add_button to the method that will handle adding the nested shelf
        add_button.bind(
            on_press=lambda x: self.add_nested_shelf(location_name, shelf_name, nested_shelf_input.text, popup))
        popup.open()

    def add_nested_shelf(self, location_name, shelf_name, nested_shelf_name, popup):
        """Add a new nested shelf to the specified shelf in the JSON structure."""
        data = self.load_json_data()

        # Check if the nested shelf already exists
        if nested_shelf_name in data["locations"][location_name][shelf_name]:
            self.status_label.text = f"Nested shelf '{nested_shelf_name}' already exists in '{shelf_name}'."
        else:
            # Add the new nested shelf with an empty list for items
            data["locations"][location_name][shelf_name][nested_shelf_name] = []
            self.save_json_data(data)
            self.status_label.text = f"Nested shelf '{nested_shelf_name}' added to '{shelf_name}' successfully."

        # Refresh by closing and reopening the nested shelves popup
        popup.dismiss()
        self.view_nested_shelves_popup(location_name, shelf_name)

    def view_nested_shelves_popup(self, location_name, shelf_name):
        """Popup to view nested shelves in the selected shelf."""
        data = self.load_json_data()
        nested_shelves = data["locations"][location_name].get(shelf_name, {})

        # Create layout for displaying nested shelves
        popup_content = BoxLayout(orientation='vertical', spacing=10)

        if nested_shelves:
            for nested_shelf_name in nested_shelves.keys():
                nested_shelf_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=44)
                nested_shelf_label = Label(text=nested_shelf_name, size_hint_x=0.4)

                # Clear Shelf button
                clear_button = Button(text="Clear Shelf", size_hint_x=0.2)
                clear_button.bind(
                    on_press=lambda btn, ns=nested_shelf_name: self.confirm_clear_shelf(location_name, shelf_name, ns))

                # Scan Items button
                scan_button = Button(text="Scan Items", size_hint_x=0.2)
                scan_button.bind(
                    on_press=lambda btn, ns=nested_shelf_name: self.scan_items(location_name, shelf_name, ns))

                # Remove Nested Shelf button
                remove_button = Button(text="Remove Nested Shelf", size_hint_x=0.2)
                remove_button.bind(
                    on_press=lambda btn, ns=nested_shelf_name: self.remove_nested_shelf(location_name, shelf_name, ns,
                                                                                        popup))

                nested_shelf_box.add_widget(nested_shelf_label)
                nested_shelf_box.add_widget(clear_button)
                nested_shelf_box.add_widget(scan_button)
                nested_shelf_box.add_widget(remove_button)
                popup_content.add_widget(nested_shelf_box)
        else:
            popup_content.add_widget(Label(text=f"No nested shelves in '{shelf_name}'."))

        # Add "Add Nested Shelf" button and close button
        add_nested_shelf_button = Button(text="Add New Nested Shelf", size_hint=(1, 0.2))
        add_nested_shelf_button.bind(on_press=lambda x: self.add_nested_shelf_popup(location_name, shelf_name))
        popup_content.add_widget(add_nested_shelf_button)

        close_button = Button(text="Close", size_hint=(1, 0.2))
        popup_content.add_widget(close_button)

        # Display the popup
        popup = Popup(title=f"Nested Shelves in {shelf_name}", content=popup_content, size_hint=(0.8, 0.8))
        close_button.bind(on_press=popup.dismiss)
        popup.open()

    def remove_nested_shelf(self, location_name, shelf_name, nested_shelf_name, popup):
        """Remove the specified nested shelf from the JSON structure."""
        data = self.load_json_data()
        if nested_shelf_name in data["locations"][location_name][shelf_name]:
            del data["locations"][location_name][shelf_name][nested_shelf_name]
            self.save_json_data(data)
            self.status_label.text = f"Nested shelf '{nested_shelf_name}' removed from '{shelf_name}' successfully."

        # Refresh the nested shelves popup
        popup.dismiss()
        self.view_nested_shelves_popup(location_name, shelf_name)

    def scan_items(self, location_name, shelf_name, nested_shelf_name):
        """Use the camera to scan and continuously add items to the specified nested shelf."""

        def handle_barcode_data(barcode_data):
            self.process_scanned_item(barcode_data, location_name, shelf_name, nested_shelf_name)

        # Set up the CameraScanner widget with handle_barcode_data as the callback
        scanner_widget = CameraScanner(scan_callback=handle_barcode_data)

        # Add a Manual Entry button
        popup_content = BoxLayout(orientation='vertical')
        popup_content.add_widget(scanner_widget)
        manual_entry_button = Button(text="Manual Entry", size_hint=(1, 0.1))
        manual_entry_button.bind(
            on_press=lambda x: self.manual_entry_popup(location_name, shelf_name, nested_shelf_name, scanner_widget))
        popup_content.add_widget(manual_entry_button)

        # Add a Close button
        close_button = Button(text="Close", size_hint=(1, 0.1))
        close_button.bind(on_press=lambda x: scanner_popup.dismiss())
        popup_content.add_widget(close_button)

        # Display the camera scanner in a popup with the Manual Entry and Close buttons
        scanner_popup = Popup(title="Scan Items", content=popup_content, size_hint=(0.9, 0.9))
        scanner_popup.bind(on_dismiss=lambda x: scanner_widget.release_camera())
        scanner_popup.open()

    def manual_entry_popup(self, location_name, shelf_name, nested_shelf_name, scanner_widget):
        """Open a popup to manually enter the order number and line number."""
        # Pause the camera while entering data manually
        scanner_widget.pause_camera()

        popup_content = BoxLayout(orientation='vertical', spacing=10)
        order_input = TextInput(hint_text="Enter order number", multiline=False)
        line_input = TextInput(hint_text="Enter line number", multiline=False)
        submit_button = Button(text="Submit", size_hint=(1, 0.2))

        popup_content.add_widget(order_input)
        popup_content.add_widget(line_input)
        popup_content.add_widget(submit_button)

        manual_popup = Popup(title="Manual Entry", content=popup_content, size_hint=(0.6, 0.4))

        def on_submit(instance):
            # Combine order number and line number, then process as scanned item
            manual_barcode = f"{order_input.text}-{line_input.text}"
            self.process_scanned_item(manual_barcode, location_name, shelf_name, nested_shelf_name)
            manual_popup.dismiss()
            scanner_widget.resume_camera()  # Resume the camera after entering data

        # Bind the submit button to process the entry and close the popup
        submit_button.bind(on_press=on_submit)
        manual_popup.bind(
            on_dismiss=lambda x: scanner_widget.resume_camera())  # Ensure camera resumes if popup is closed

        # Open the manual entry popup
        manual_popup.open()

    def process_barcode(self, barcode_data, callback):
        """Process barcode data to ensure consistent format."""
        if "-" in barcode_data:
            # Barcode is already in the correct format
            callback(barcode_data)
        else:
            # Barcode missing hyphen; prompt for line number
            order_number = barcode_data[:10]  # First 10 digits as order number
            self.prompt_line_number(order_number, callback)

    def prompt_line_number(self, order_number, callback):
        """Prompt the user to enter a line number and process the item with it."""

        # Ensure line_popup is cleared and create a new popup instance
        if hasattr(self, 'line_popup'):
            self.line_popup.dismiss()  # Dismiss any existing instance

        line_popup_content = BoxLayout(orientation='vertical')
        line_input = TextInput(hint_text="Enter line number", focus=True)
        submit_button = Button(text="Submit")

        line_popup_content.add_widget(line_input)
        line_popup_content.add_widget(submit_button)

        self.line_popup = Popup(title="Enter Line Number", content=line_popup_content, size_hint=(0.6, 0.4))

        # Bind submit button to finalize_barcode and dismiss the popup after processing
        submit_button.bind(
            on_press=lambda x: self.finalize_barcode(order_number, line_input.text, callback, self.line_popup))

        # Bind a confirmation print to ensure popup is opened and dismissed correctly
        self.line_popup.bind(on_open=lambda x: print("Line number popup opened."))
        self.line_popup.bind(on_dismiss=lambda x: print("Line number popup dismissed."))

        self.line_popup.open()

    def finalize_barcode(self, order_number, line_number, callback, popup):
        """Combine order number and line number, call the callback, and dismiss the popup."""
        processed_barcode = f"{order_number}-{line_number}"
        print(f"Finalized barcode: {processed_barcode}")  # Debug: check processed barcode
        callback(processed_barcode)
        popup.dismiss()  # Dismiss the popup after processing
        print("Popup dismissed.")  # Debug: confirm popup dismissal

    def set_line_number(self, line_number, popup):
        """Set the line number and dismiss the popup."""
        self._line_number = line_number
        popup.dismiss()

    def process_scanned_item(self, barcode_data, location_name, shelf_name, nested_shelf_name):
        """Process scanned barcode and add/move the item to the nested shelf."""

        def on_barcode_processed(parsed_barcode):
            # Existing logic to handle moving or adding the parsed barcode
            data = self.load_json_data()
            item_found = False

            # Check if item exists elsewhere and move if necessary
            for loc, shelves in data["locations"].items():
                for sh, nested_shelves in shelves.items():
                    for ns, items in nested_shelves.items():
                        if parsed_barcode in items:
                            items.remove(parsed_barcode)
                            self.status_label.text = f"Item '{parsed_barcode}' moved from '{ns}' in '{sh}'."
                            item_found = True
                            break
                    if item_found:
                        break
                if item_found:
                    break

            # Add the item to the new nested shelf
            nested_shelf = data["locations"][location_name][shelf_name][nested_shelf_name]
            nested_shelf.append(parsed_barcode)
            self.save_json_data(data)
            self.status_label.text = f"Item '{parsed_barcode}' moved to '{nested_shelf_name}' in '{shelf_name}'."

        # Call process_barcode with the barcode data and the callback
        self.process_barcode(barcode_data, on_barcode_processed)

    # def move_item(self, scanned_item_id, new_location_name, new_shelf_name, new_nested_shelf_name):
    #     """Move the specified item to a new nested shelf if it exists elsewhere."""
    #     data = self.load_json_data()
    #     item_found = False
    #
    #     # Search for the item in all locations, shelves, and nested shelves
    #     for loc, shelves in data["locations"].items():
    #         for sh, nested_shelves in shelves.items():
    #             for ns, items in nested_shelves.items():
    #                 if scanned_item_id in items:
    #                     # Remove the item from its current nested shelf
    #                     items.remove(scanned_item_id)
    #                     self.status_label.text = f"Item '{scanned_item_id}' moved from '{ns}' in '{sh}'."
    #                     item_found = True
    #                     break
    #             if item_found:
    #                 break
    #         if item_found:
    #             break
    #
    #     # Add the item to the new nested shelf
    #     data["locations"][new_location_name][new_shelf_name][new_nested_shelf_name].append(scanned_item_id)
    #     self.save_json_data(data)
    #     self.status_label.text = f"Item '{scanned_item_id}' moved to '{new_nested_shelf_name}' in '{new_shelf_name}'."

    def clear_shelf(self, location_name, shelf_name, nested_shelf_name, confirmation_popup):
        """Clear all items from the specified nested shelf without deleting the shelf."""
        data = self.load_json_data()

        # Access the nested shelf and clear its items
        nested_shelf = data["locations"][location_name][shelf_name].get(nested_shelf_name, [])
        if nested_shelf:
            nested_shelf.clear()
            self.save_json_data(data)
            self.status_label.text = f"Cleared all items from '{nested_shelf_name}' in '{shelf_name}'."
        else:
            self.status_label.text = f"No items to clear in '{nested_shelf_name}'."

        # Close the confirmation popup after clearing
        confirmation_popup.dismiss()

    def confirm_clear_shelf(self, location_name, shelf_name, nested_shelf_name):
        """Popup to confirm clearing all items from a nested shelf."""
        popup_content = BoxLayout(orientation='vertical', spacing=10)
        popup_content.add_widget(Label(
            text=f"Are you sure you want to clear all items from '{nested_shelf_name}' in '{shelf_name}'? This cannot be undone."))

        # Define the popup first so we can reference it within button bindings
        confirmation_popup = Popup(title="Confirm Clear Shelf", content=popup_content, size_hint=(0.8, 0.4))

        # Yes button to confirm clearing
        yes_button = Button(text="Yes", size_hint=(1, 0.2))
        yes_button.bind(
            on_press=lambda x: self.clear_shelf(location_name, shelf_name, nested_shelf_name, confirmation_popup))

        # No button to cancel
        no_button = Button(text="No", size_hint=(1, 0.2))
        no_button.bind(on_press=confirmation_popup.dismiss)

        popup_content.add_widget(yes_button)
        popup_content.add_widget(no_button)

        # Display the confirmation popup
        confirmation_popup.open()






