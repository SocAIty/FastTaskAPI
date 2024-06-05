"""
UploadDataTypes are used to ensure compatibility between different providers. For example:
- fastapi has built in data types like "UploadFile", "File" which can be configured in detail and can be arbitrary.
- In runpod the job data always is json. Therefore, any upload data must be base64 encoded.
We will parse the data and always provide it as a binary object to your function.
"""
import base64
from enum import Enum
from inspect import Parameter
from typing import Union

from starlette.datastructures import UploadFile as StarletteUploadFile


class UploadDataType(Enum):
    """
    Use the dataypes to ensure compatibility between different providers.
    Under the hood socaity_router will parse the data and provide it to your function in the correct format.
    """
    FILE = "file"  # Literally any file encoded as binary
    IMAGE = "image"  # An image file. We will decode with opencv
    AUDIO = "audio"  # An audio file. We will decode with librosa
    VIDEO = "video"  # A video file. We will decode with opencv


class UploadFile:
    def __init__(self, content: bytes, file_type: str, file_name: str):
        self.content = content
        self.file_type = file_type
        self.file_name = file_name


class imageFile(UploadFile):
    """
    A class to represent an image file.
    """

    def __init__(self, image_data: bytes, file_type: str):
        self.image_data = image_data
        self.file_type = file_type


def starlette_uploadfile_to_socaity_upload_file(
        file: Union[StarletteUploadFile, str, bytes],
        target_s_upload_type: UploadDataType
):
    file_name = None
    file_type = None
    if isinstance(file, StarletteUploadFile):
        content = file.file.read()
        file_name = file.filename
        file_type = file.content_type
    elif isinstance(file, str):
        content = base64_to_file(file, file_type=target_s_upload_type)
    else:
        content = file

    # ToDo: add native image support
    # if target_s_upload_type == UploadDataType.FILE:
    #    return UploadFile(file=content, file_type="file", file_name=file.filename)
    # elif target_s_upload_type == UploadDataType.IMAGE:
    #    return imageFile(image_data=content, file_type="image")

    return UploadFile(content=content, file_type=file_type, file_name=file_name)


def base64_to_file(base64_str: str, file_type: UploadDataType = None):
    """
    Convert a base64 string to a file.
    :param base64_str: The base64 string
    :param file_path: The path to save the file
    :return: None
    """
    # debug code
    # with open("requirements.txt", "rb") as f:
    #    base64_str = f.read()
    #  data = base64.b64encode(base64_str).decode('ascii')
    # file = io.BytesIO(data)
    # from fastapi import UploadFile
    # uf = UploadFile(file=file)
    # TODO: Unify those things.

    data = base64.b64decode(base64_str.encode('ascii'))
    # write data to virtual file with BytesIO
    return data


def is_param_upload_file(param: Parameter):
    """
    Check if a parameter is a file upload.
    """
    from fastapi import UploadFile as fastapiUploadFile
    type_check_list = [UploadDataType, UploadFile, StarletteUploadFile, fastapiUploadFile]
    return type(param.annotation) in type_check_list or param.annotation in type_check_list


def convert_UploadDataType_to_FastAPI_UploadFile(param: Parameter):
    """
    Convert a UploadDataType to a FastAPI UploadFile type.
    """
    from fastapi import UploadFile as fastapiUploadFile
    param_annotation_conversion_dict = {
        UploadDataType.FILE: fastapiUploadFile,
        UploadDataType.IMAGE: fastapiUploadFile,
        UploadDataType.AUDIO: fastapiUploadFile,
        UploadDataType.VIDEO: fastapiUploadFile,
        UploadFile: fastapiUploadFile,
        StarletteUploadFile: fastapiUploadFile,
        fastapiUploadFile: fastapiUploadFile
    }

    if param.annotation not in param_annotation_conversion_dict:
        raise Exception(f"UploadDataType {param.annotation} not supported in FastAPI")

    return param.replace(annotation=param_annotation_conversion_dict[param.annotation])
