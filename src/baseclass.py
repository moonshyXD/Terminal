import logging
import os

from errors import Error


class BaseClass:
    def __init__(self):
        pass

    def _abs_path(self, path: str) -> str:
        if not os.path.isabs(path):
            abs_path = os.path.join(os.getcwd(), path)
        else:
            abs_path = path

        return abs_path

    def _path_exists(self, path: str, command: str) -> None:
        if not os.path.exists(path):
            log = (
                f"Command: {command}\n",
                "Status: ERROR\n",
                f"Message: no such file in path: {path}\n",
            )
            logging.error(log)
            raise Error(log)

    def _is_file(self, path: str, command: str):
        if os.path.isdir(path):
            log = (
                f"Command: {command}\n",
                "Status: ERROR\n",
                f"Message: file {path} is a directory\n",
            )
            logging.error(log)
            return Error

    def _is_directory(self, path: str, command: str):
        if os.path.isdir(path):
            log = (
                f"Command: {command}\n",
                "Status: ERROR\n",
                f"Message: file {path} is a directory\n",
            )
            logging.error(log)
            return Error
