import io
from typing import Union

from socaity_router.compatibility.upload_file import UploadFile

class AudioFile(UploadFile):
    """
    Has file conversions that make it easy to work with image files across the web.
    Internally it uses numpy and librosa.
    """
    def from_file(self, path_or_handle: Union[str, io.BytesIO, io.BufferedReader]):
        import librosa
        import numpy as np
        self._reset_buffer()
        y, sr = librosa.load(path_or_handle, sr=None)
        np.save(self._content_buffer, y)
        self._content_buffer.seek(0)

    def to_audio(self):
        import numpy as np
        self._content_buffer.seek(0)
        y = np.load(self._content_buffer)
        return y

    @staticmethod
    def _necessary_libs_installed():
        try:
            import librosa
            import numpy as np
            return True
        except ImportError:
            return False

    @staticmethod
    def _get_necessary_libs() -> list:
        return ["librosa", "numpy"]