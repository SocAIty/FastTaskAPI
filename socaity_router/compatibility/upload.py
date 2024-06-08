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

from socaity_router.compatibility.audio_file import AudioFile
from socaity_router.compatibility.image_file import ImageFile
from socaity_router.compatibility.upload_file import UploadFile
from socaity_router.compatibility.video_file import VideoFile


def _print_import_warning(class_name: str, lib_names: list):
    print(f"Necessary libraries: {', '.join(lib_names)} are not installed. "
          f"Please install them before using the {class_name} class.")


class UploadDataType(Enum):
    """
    Use the dataypes to ensure compatibility between different providers.
    Under the hood socaity_router will parse the data and provide it to your function in the correct format.
    """
    FILE = "file"  # Literally any file encoded as binary
    IMAGE = "image"  # An image file. We will decode with opencv
    AUDIO = "audio"  # An audio file. We will decode with librosa
    VIDEO = "video"  # A video file. We will decode with opencv


def get_upload_file_class(
        target_upload_file: Union[UploadDataType, UploadFile, ImageFile, AudioFile, VideoFile]
) -> Union[UploadFile, ImageFile, AudioFile, VideoFile]:
    target_upload_types = {
        UploadDataType.FILE: UploadFile,
        UploadDataType.IMAGE: ImageFile,
        UploadDataType.AUDIO: AudioFile,
        UploadDataType.VIDEO: VideoFile
    }
    if target_upload_file in target_upload_types:
        target_upload_file = target_upload_types[target_upload_file]

    # check for libs
    if not target_upload_file._necessary_libs_installed():
        _print_import_warning(target_upload_file.__name__, target_upload_file._get_necessary_libs())
        target_upload_file = UploadFile

    return target_upload_file


def read_file_content_as_binary(file: Union[StarletteUploadFile, str, bytes]) -> bytes:
    """
    Read a file to binary.
    :param file: The file to read. Can be a StarletteUploadFile, a base64 string or binary data.
    :return: The binary data.
    """
    if isinstance(file, StarletteUploadFile):
        return file.file.read()
    elif isinstance(file, str):
        return base64_to_binary_file(file)
    else:
        return file


def starlette_uploadfile_to_socaity_upload_file(
        file: Union[StarletteUploadFile, str, bytes],
        target_upload_file: UploadDataType
):
    # get class ref like UploadFile, ImageFile, AudioFile, VideoFile
    target_upload_file_class = get_upload_file_class(target_upload_file)

    # get content, file_name and file_type
    file_name = None
    file_type = None
    content = read_file_content_as_binary(file)

    instantiated_file = target_upload_file_class(file_name=file_name, file_type=file_type)
    instantiated_file.from_binary(content)
    return instantiated_file
    #if isinstance(file, StarletteUploadFile):
    #    content = file.file.read()
    #    file_name = file.filename
    #    file_type = file.content_type
    #elif isinstance(file, str):
    #    content = base64_to_file(file, file_type=target_upload_file)
    #else:
    #    content = file


    # Create File



    #if target_upload_file == UploadDataType.FILE:
    #    return UploadFile(file=content, file_type="file", file_name=file.filename)
    #elif target_upload_file == UploadDataType.IMAGE:
    #    if not ImageFile._necessary_libs_installed():
    #        _print_import_warning("ImageFile", ["opencv-python", "numpy"])
    #        return UploadFile(content=content, file_type="file", file_name=file_name)
    #    else:
    #        return ImageFile(image_data=content, file_type="image")
    #elif target_upload_file == UploadDataType.AUDIO:
    #    if not AudioFile._necessary_libs_installed():
    #        _print_import_warning("AudioFile", ["librosa", "numpy"])
    #        return UploadFile(content=content, file_type="file", file_name=file_name)
    #    else:
    #        return AudioFile(audio_data=content, file_type="audio")
#
    ##    return imageFile(image_data=content, file_type="image")
#
    #return UploadFile(content=content, file_type=file_type, file_name=file_name)


def base64_to_binary_file(base64_str: str):
    """
    Convert a base64 string to a binary file.
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
    type_check_list = [
        UploadDataType, UploadFile, ImageFile, AudioFile, VideoFile,
        StarletteUploadFile, fastapiUploadFile
    ]
    return type(param.annotation) in type_check_list or param.annotation in type_check_list


def convert_param_type_to_fast_api_upload_file(param: Parameter):
    """
    Convert a UploadDataType to a FastAPI UploadFile type.
    """
    from fastapi import UploadFile as fastapiUploadFile
    return param.replace(annotation=fastapiUploadFile)
