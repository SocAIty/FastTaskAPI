from socaity_router.compatibility.upload_file import UploadFile

try:
    import cv2
    import numpy as np
except ImportError:
    pass


class ImageFile(UploadFile):
    """
    Has file conversions that make it easy to work with image files across the web.
    Internally it uses cv2 file format.
    """
    def from_bytes(self, data: bytes):
        super().from_bytes(data)
        self._detect_image_type(self.to_np_array())

    def from_np_array(self, np_array: np.array):
        super().from_np_array(np_array)
        self._detect_image_type(np_array)

    def from_base64(self, base64_str: str):
        super().from_base64(base64_str)
        self._detect_image_type(self.to_np_array())

    def to_np_array(self):
        bytes = self.to_bytes()
        return cv2.imdecode(np.frombuffer(bytes, np.uint8), -1)

    def to_cv2_img(self):
        return self.to_np_array()

    def save(self, path: str):
        cv2.imwrite(path, self.to_np_array())

    def _detect_image_type(self, np_array: np.array):
        img_type, channels = self.detect_image_type_and_channels(np_array)
        if img_type is not None:
            self.content_type = f"image/{img_type}"

    @staticmethod
    def detect_image_type_and_channels(image) -> (str, int):
        """Detect the image type and number of _channels from a numpy array."""
        # Check the number of _channels
        if len(image.shape) == 2:
            channels = 1  # Grayscale
        elif len(image.shape) == 3:
            channels = image.shape[2]
        else:
            #raise ValueError("Unsupported image shape: {}".format(image.shape))
            return None, None

        # Detect image type by checking for specific markers
        image_type = None

        # Convert to bytes and inspect file signatures for format detection
        success, encoded_image = cv2.imencode('.png', image)
        if success:
            encoded_bytes = encoded_image.tobytes()
            if encoded_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
                image_type = 'png'
            elif encoded_bytes[0:2] == b'\xff\xd8':
                image_type = 'jpeg'
            elif encoded_bytes.startswith(b'BM'):
                image_type = 'bmp'
            elif encoded_bytes.startswith(b'GIF'):
                image_type = 'gif'

        return image_type, channels


    @staticmethod
    def _necessary_libs_installed() -> bool:
        try:
            import cv2
            import numpy as np
            return True
        except ImportError:
            return False

    @staticmethod
    def _get_necessary_libs() -> list:
        return ["opencv-python", "numpy"]
