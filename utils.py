import os
import uuid


def generate_filename(filename: str) -> str:
    """
        The method generates a unique name for the file
        :param filename: filename of file
        :return: string unique filename
    """
    unique = uuid.uuid4()
    _filename = f'{filename}_{unique}'
    if os.path.exists(_filename):
        return generate_filename(filename)
    return _filename
