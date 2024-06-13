import base64
import io
import mimetypes
from typing import Union
import os


try:
    import numpy as np
except ImportError:
    pass


class UploadFile:
    """
    Has file conversions that make it easy to work standardized with files across the web and in the sdk.
    Works natively with bytesio, base64 and binary data.
    """
    def __init__(self):
        self.content_type = "application/octet-stream"
        self.file_name = "file"
        self._content_buffer = io.BytesIO()

    def set_content(self, buffer: io.BytesIO, path_or_handle: Union[str, io.BytesIO, io.BufferedReader]):
        # read buffer
        self._reset_buffer()
        if isinstance(buffer, io.BytesIO):
            self._content_buffer.write(buffer.read())
            self._content_buffer.seek(0)
        elif isinstance(buffer, io.BufferedReader):
            self._content_buffer = buffer

        # set file name and type
        self.file_name = path_or_handle if isinstance(path_or_handle, str) else path_or_handle.name
        self.file_name = os.path.basename(self.file_name)
        self.content_type = mimetypes.guess_type(self.file_name)[0] or "application/octet-stream"

    def from_file(self, path_or_handle: Union[str, io.BytesIO, io.BufferedReader]):
        """
        Load a file from a file path, file handle or base64 and convert it to BytesIO.
        """
        if type(path_or_handle) in [io.BufferedReader, io.BytesIO]:
            self.set_content(path_or_handle, path_or_handle)
        elif isinstance(path_or_handle, str):
            # read file from path
            with open(path_or_handle, 'rb') as file:
                self.set_content(file, path_or_handle)
                self.file_name = file.name

        return self

    def from_bytes(self, data: bytes):
        self._reset_buffer()
        self._content_buffer.write(data)
        self._content_buffer.seek(0)
        return self

    def to_bytes(self) -> bytes:
        self._content_buffer.seek(0)
        return self._content_buffer.read()

    @staticmethod
    def _decode_base_64_if_is(data: str):
        """
        Checks if a string is base64. If it is it returns the decoded string; else returns None
        """
        # wie just encode the string and encode it back. If backencoding is the same string it was base64
        decoded = base64.b64decode(data)
        back_encoded = base64.b64encode(data)
        if back_encoded == decoded:
            return data
        else:
            return None

    def from_base64(self, base64_str: str):
        decoded = self._decode_base_64_if_is(base64_str)
        if decoded is not None:
            return self.from_bytes(base64.b64decode(base64_str))
        else:
            raise ValueError("Decoding from base64 like string was not possible. Check your data.")

    def to_base64(self):
        return base64.b64encode(self.to_bytes()).decode()

    def from_np_array(self, np_array):
        self._reset_buffer()
        np.save(self._content_buffer, np_array)
        self._content_buffer.seek(0)
        return self

    def to_np_array(self):
        self._content_buffer.seek(0)
        return np.load(self._content_buffer)

    def to_httpx_send_able_tuple(self):
        return self.file_name, self.read(), self.content_type

    def _reset_buffer(self):
        self._content_buffer.seek(0)
        self._content_buffer.truncate(0)

    def read(self):
        self._content_buffer.seek(0)
        return self._content_buffer.read()

    def save(self, path: str):
        with open(self.file_name, 'wb') as file:
            file.write(self.read())

    def __bytes__(self):
        return self.to_bytes()

    def __array__(self):
        return self.to_np_array()


    @staticmethod
    def _necessary_libs_installed() -> bool:
        return True

    @staticmethod
    def _get_necessary_libs() -> list:
        return []
