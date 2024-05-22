"""
UploadDataTypes are used to ensure compatibility between different providers. For example:
- fastapi has built in data types like "UploadFile", "File" which can be configured in detail and can be arbitrary.
- In runpod the job data always is json. Therefore, any upload data must be base64 encoded.
We will parse the data and always provide it as a binary object to your function.
"""
import base64
from enum import Enum
from inspect import Parameter
import io


class UploadDataType(Enum):
    """
    Use the dataypes to ensure compatibility between different providers.
    Under the hood socaity_router will parse the data and provide it to your function in the correct format.
    """
    FILE = "file"  # Literally any file encoded as binary
    IMAGE = "image"  # An image file. We will decode with opencv
    AUDIO = "audio"  # An audio file. We will decode with librosa
    VIDEO = "video"  # A video file. We will decode with opencv



def base64_to_file(base64_str: str, file_type: UploadDataType = None):
    """
    Convert a base64 string to a file.
    :param base64_str: The base64 string
    :param file_path: The path to save the file
    :return: None
    """
    # debug code
    #with open("requirements.txt", "rb") as f:
    #    base64_str = f.read()
    #  data = base64.b64encode(base64_str).decode('ascii')
    # file = io.BytesIO(data)
    # from fastapi import UploadFile
    # uf = UploadFile(file=file)
    # TODO: Unify those things.

    data = base64.b64decode(base64_str.encode('ascii'))
    # write data to virtual file with BytesIO
    return data

    #if file_type == UploadDataType.IMAGE:
    #    # TODO: Implement different data types. Create a new utils package so that dependencies are not blown up.
    #    import numpy as np
    #    import cv2
    #    image_array = np.frombuffer(data, np.uint8)
    #    data = cv2.imdecode(image_array, cv2.IMREAD_COLOR)  # im_arr: image in Numpy one-dim array format.
#
    #return data


def convert_UploadDataType_to_FastAPI_UploadFile(param: Parameter):
    """
    Convert a UploadDataType to a FastAPI UploadFile type.
    """
    from fastapi import File, UploadFile
    param_annotation_conversion_dict = {
        UploadDataType.FILE: UploadFile,
        UploadDataType.IMAGE: UploadFile,
        UploadDataType.AUDIO: UploadFile,
        UploadDataType.VIDEO: UploadFile
    }

    if param.annotation not in param_annotation_conversion_dict:
        raise Exception(f"UploadDataType {param.annotation} not supported in FastAPI")

    return param.replace(annotation=param_annotation_conversion_dict[param.annotation])


