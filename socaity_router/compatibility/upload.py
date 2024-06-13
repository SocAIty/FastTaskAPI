"""
UploadDataTypes are used to ensure compatibility between different providers. For example:
- fastapi has built in data types like "UploadFile", "File" which can be configured in detail and can be arbitrary.
- In runpod the job data always is json. Therefore, any upload data must be base64 encoded.
We will parse the data and always provide it as a binary object to your function.
"""
import base64
from inspect import Parameter
from typing import Union

from socaity_router.compatibility.audio_file import AudioFile
from socaity_router.compatibility.image_file import ImageFile
from socaity_router.compatibility.upload_file import UploadFile
from socaity_router.compatibility.video_file import VideoFile
from fastapi import UploadFile as fastapiUploadFile
from starlette.datastructures import UploadFile as StarletteUploadFile

def _print_import_warning(class_name: str, lib_names: list):
    print(f"Necessary libraries: {', '.join(lib_names)} are not installed. "
          f"Please install them before using the {class_name} class.")


def get_upload_file_class(
        target_upload_file: Union[UploadFile, ImageFile, AudioFile, VideoFile, fastapiUploadFile]
) -> Union[UploadFile, ImageFile, AudioFile, VideoFile]:
    """
    Get the class reference for the upload file.
    :param target_upload_file: What was specified in the app.add_route function.
    :param content_type: the data type of the file transmitted by upload.
    :return:
    """

    target_upload_types = {
        fastapiUploadFile: UploadFile,
        StarletteUploadFile: UploadFile
    }

    if issubclass(target_upload_file, UploadFile):
        target_upload_file = target_upload_file
    elif target_upload_file in target_upload_types:
        target_upload_file = target_upload_types[target_upload_file]
    else:
        target_upload_file = UploadFile

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
        target_upload_file: Union[UploadFile, ImageFile, AudioFile, VideoFile, fastapiUploadFile]
):
    # get class ref like UploadFile, ImageFile, AudioFile, VideoFile
    target_upload_file_class = get_upload_file_class(target_upload_file)

    # get content, file_name and content_type
    content = read_file_content_as_binary(file)

    instantiated_file: UploadFile = target_upload_file_class()
    instantiated_file.file_name = file.filename
    instantiated_file.content_type = file.content_type
    instantiated_file.from_bytes(content)
    return instantiated_file


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
        UploadFile, ImageFile, AudioFile, VideoFile,
        StarletteUploadFile, fastapiUploadFile
    ]
    return type(param.annotation) in type_check_list or param.annotation in type_check_list


def convert_param_type_to_fast_api_upload_file(param: Parameter):
    """
    Convert a UploadDataType to a FastAPI UploadFile type.
    """
    from fastapi import UploadFile as fastapiUploadFile
    return param.replace(annotation=fastapiUploadFile)
