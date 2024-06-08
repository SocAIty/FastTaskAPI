import os.path

from socaity.socaity_client.web.req.upload_files.upload_file import UploadFile
import base64
import io


class ImageFile(UploadFile):
    """
    Has file conversions that make it easy to work with image files across the web.
    Internally it uses cv2 file format.
    """
    def from_file(self, path_or_handle: str):
        import cv2
        img = cv2.imread(path_or_handle)
        self.set_content(img, path_or_handle)

    def from_bytes(self, binary_data: bytes):
        import cv2
        import numpy as np
        # parse bytes to cv2.imread
        img = cv2.imdecode(np.frombuffer(binary_data, np.uint8), -1)
        self.set_content(img, path_or_handle=None)

    def to_bytes_io(self) -> io.BytesIO:
        import cv2
        # encode image to binary
        is_success, buf = cv2.imencode(f".{self.file_type}", self.content)
        return io.BytesIO(buf)

    def to_base64(self):
        return self.content

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
