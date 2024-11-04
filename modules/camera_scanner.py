import cv2
from pyzbar.pyzbar import decode
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.clock import Clock


class CameraScanner(Image):
    def __init__(self, scan_callback, **kwargs):
        super().__init__(**kwargs)
        self.scan_callback = scan_callback
        self.capture = cv2.VideoCapture(0)  # Initialize camera (default camera index is 0)
        Clock.schedule_interval(self.update, 1.0 / 30)  # 30 frames per second

    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            # Convert to grayscale for better contrast
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            barcodes = decode(gray_frame)
            for barcode in barcodes:
                barcode_data = barcode.data.decode("utf-8")
                self.scan_callback(barcode_data)  # Call the callback function with barcode data

            # Convert the frame to texture for display
            buf = cv2.flip(frame, 0).tostring()
            image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt="luminance")
            image_texture.blit_buffer(buf, colorfmt="luminance", bufferfmt="ubyte")
            self.texture = image_texture

            # Process frame to detect barcodes
            barcodes = decode(frame)
            for barcode in barcodes:
                barcode_data = barcode.data.decode("utf-8")
                self.scan_callback(barcode_data)  # Call the callback function with barcode data

            # Convert the frame to texture for display
            buf = cv2.flip(frame, 0).tostring()
            image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt="bgr")
            image_texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
            self.texture = image_texture

    def pause_camera(self):
        """Pause the camera feed temporarily."""
        self.camera_active = False

    def resume_camera(self):
        """Resume the camera feed after pausing."""
        self.camera_active = True

    def release_camera(self):
        """Release the camera when done scanning."""
        if self.capture.isOpened():
            self.capture.release()

    def on_stop(self):
        """Release resources when widget is stopped."""
        self.release_camera()