"""
UploadDataTypes are used to ensure compatibility between different providers. For example:
- fastapi has built in data types like "MultiModalFile", "File" which can be configured in detail and can be arbitrary.
- In runpod the job data always is json. Therefore, any upload data must be base64 encoded.
We will parse the data and always provide it as a binary object to your function.
"""
from inspect import Parameter
from multimodal_files import MultiModalFile, AudioFile, ImageFile, VideoFile
from starlette.datastructures import UploadFile as StarletteUploadFile


def _print_import_warning(class_name: str, lib_names: list):
    print(f"Necessary libraries: {', '.join(lib_names)} are not installed. "
          f"Please install them before using the {class_name} class.")

def is_param_multimodal_file(param: Parameter):
    """
    Check if a parameter is a file upload.
    """
    if param is None:
        return False

    from fastapi import UploadFile as fastapiUploadFile
    type_check_list = [
        MultiModalFile, ImageFile, AudioFile, VideoFile,
        StarletteUploadFile, fastapiUploadFile
    ]
    if not hasattr(param, 'annotation'):
        if not any(isinstance(param, t) for t in type_check_list):
            return False
        else:
            return True

    return type(param.annotation) in type_check_list or param.annotation in type_check_list


def convert_param_type_to_fast_api_upload_file(param: Parameter):
    """
    Convert a UploadDataType to a FastAPI MultiModalFile type.
    """
    from fastapi import UploadFile as fastapiUploadFile
    return param.replace(annotation=fastapiUploadFile)
