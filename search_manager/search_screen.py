from kivy.core.audio import SoundLoader
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
import json

from modules.camera_scanner import CameraScanner  # Import your CameraScanner class

class SearchScreen(Screen):
    def __init__(self, json_file_path, **kwargs):
        super().__init__(**kwargs)
        self.json_file_path = json_file_path

        # Layout for search screen
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Input for manual entry
        self.barcode_input = TextInput(hint_text="Enter barcode manually", multiline=False)
        layout.add_widget(self.barcode_input)

        # Manual Search Button
        search_button = Button(text="Search Manually")
        search_button.bind(on_press=self.search_item)
        layout.add_widget(search_button)

        # Scan Barcode Button
        scan_button = Button(text="Scan Barcode")
        scan_button.bind(on_press=self.open_camera_popup)
        layout.add_widget(scan_button)

        # Results display
        self.result_label = Label(text="Search results will appear here.")
        layout.add_widget(self.result_label)

        # Close button to return to MainScreen
        close_button = Button(text="Close", size_hint=(1, 0.1))
        close_button.bind(on_press=self.return_to_main)
        layout.add_widget(close_button)

        self.add_widget(layout)

    def return_to_main(self, instance):
        """Return to the main screen."""
        self.manager.current = 'main'  # Assuming the main screen is named 'main'

    def load_json_data(self):
        """Utility function to load JSON data."""
        with open(self.json_file_path, 'r') as file:
            return json.load(file)

    def search_item(self, instance):
        """Initiate barcode processing for manual search."""
        barcode = self.barcode_input.text.strip()
        self.process_barcode(barcode, self.perform_search)
        self.barcode_input.text = ""

    def perform_search(self, barcode):
        """Perform the search and display results after barcode is fully processed."""
        data = self.load_json_data()
        found = False
        location_info = ""

        # Loop through the JSON structure to search for the item
        for loc_name, shelves in data.get("locations", {}).items():
            for shelf_name, nested_shelves in shelves.items():
                for nested_shelf_name, items in nested_shelves.items():
                    if barcode in items:
                        # Play the 'found' sound when item is located
                        found_beep = SoundLoader.load('./assets/found_beep.mp3')
                        if found_beep:
                            found_beep.play()
                        location_info = f"Found in {loc_name} > {shelf_name} > {nested_shelf_name}"
                        found = True
                        break
                if found:
                    break
            if found:
                break

        # Play 'not found' sound only if item was not located
        if not found:
            not_found_beep = SoundLoader.load('./assets/not_found_tone.mp3')
            if not_found_beep:
                not_found_beep.play()

        # Update the label with the search result
        self.result_label.text = location_info if found else "Item not found."

    def open_camera_popup(self, instance):
        """Open a popup with the camera to scan a barcode."""
        def handle_barcode_data(barcode_data):
            self.process_barcode(barcode_data, self.perform_search)
            scanner_popup.dismiss()  # Close the popup after scanning

        # Create CameraScanner instance
        scanner_widget = CameraScanner(scan_callback=handle_barcode_data)

        # Set up the popup with the CameraScanner
        popup_content = BoxLayout(orientation='vertical')
        popup_content.add_widget(scanner_widget)
        close_button = Button(text="Close", size_hint=(1, 0.1))
        close_button.bind(on_press=lambda x: scanner_popup.dismiss())
        popup_content.add_widget(close_button)

        # Display the popup
        scanner_popup = Popup(title="Scan Barcode", content=popup_content, size_hint=(0.9, 0.9))
        scanner_popup.bind(on_dismiss=lambda x: scanner_widget.release_camera())  # Ensure camera is released
        scanner_popup.open()

    def process_barcode(self, barcode_data, callback):
        """Process barcode data to ensure consistent format and call callback when ready."""
        if "-" in barcode_data:
            callback(barcode_data)  # Barcode already in the correct format
        else:
            # Barcode without hyphen: assume order number is the first 10 digits
            order_number = barcode_data[:10]
            self.prompt_line_number(order_number, callback)

    def prompt_line_number(self, order_number, callback):
        """Prompt the user to enter a line number if barcode lacks hyphen, return formatted barcode."""
        line_popup_content = BoxLayout(orientation='vertical')
        line_input = TextInput(hint_text="Enter line number", multiline=False)
        submit_button = Button(text="Submit")

        line_popup_content.add_widget(line_input)
        line_popup_content.add_widget(submit_button)

        line_popup = Popup(title="Enter Line Number", content=line_popup_content, size_hint=(0.6, 0.4))

        def on_submit(instance):
            line_number = line_input.text
            callback(f"{order_number}-{line_number}")
            line_popup.dismiss()

        submit_button.bind(on_press=on_submit)
        line_popup.open()
