import argparse
import logging
import os
from abc import ABC, abstractmethod
from typing import Any

from src.errors import NotADirectoryError, NotAFileError, PathNotFoundError


class BaseClass(ABC):
    _command: str = ""

    def __init__(self):
        self._command = self.__class__.__name__.lower()

    @property
    def command(self) -> str:
        return self._command

    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> None:
        pass

    def _abs_path(self, path: str) -> str:
        if path == "~":
            return os.path.expanduser("~")
        elif path == "..":
            return os.path.dirname(os.getcwd())

        if not os.path.isabs(path):
            return os.path.join(os.getcwd(), path)

        return path

    def _path_exists(self, path: str) -> None:
        if not os.path.exists(path):
            raise PathNotFoundError(
                f"No such file or directory {path}"
            ) from None

    def _is_file(self, path: str):
        if not os.path.isfile(path):
            raise NotAFileError(f"Not a file: {path}") from None

    def _is_directory(self, path: str):
        if not os.path.isdir(path):
            raise NotADirectoryError(f"Not a directory: {path}") from None

    def _is_tokens(self, tokens: argparse.Namespace):
        if not tokens.paths:
            message = "Missing file operand"
            logging.error(message)
            raise PathNotFoundError(message) from None
