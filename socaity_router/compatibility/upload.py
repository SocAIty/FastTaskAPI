"""
UploadDataTypes are used to ensure compatibility between different providers. For example:
- fastapi has built in data types like "UploadFile", "File" which can be configured in detail and can be arbitrary.
- In runpod the job data always is json. Therefore, any upload data must be base64 encoded.
We will parse the data and always provide it as a binary object to your function.
"""
from inspect import Parameter
from multimodal_files import UploadFile, AudioFile, ImageFile, VideoFile
from starlette.datastructures import UploadFile as StarletteUploadFile


def _print_import_warning(class_name: str, lib_names: list):
    print(f"Necessary libraries: {', '.join(lib_names)} are not installed. "
          f"Please install them before using the {class_name} class.")

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
