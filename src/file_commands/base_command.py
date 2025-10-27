import argparse
import logging
import os
from abc import ABC, abstractmethod

from src.errors import (
    InvalidPathError,
    NotADirectoryError,
    NotAFileError,
    PathNotFoundError,
)


class BaseClass(ABC):
    _command: str = ""

    def __init__(self):
        self._command = self.__class__.__name__.lower()

    @property
    def command(self) -> str:
        return self._command

    @abstractmethod
    def execute(self, tokens: argparse.Namespace) -> None:
        pass

    def _abs_path(self, path: str) -> str:
        if path == "~":
            return os.path.expanduser("~")
        elif path == "..":
            return os.path.dirname(os.getcwd())

        if not os.path.isabs(path):
            return os.path.join(os.getcwd(), path)

        return path

    def _correct_path(self, path: str):
        broken_list = ["#", "&", "(", ")", "*", "?", "'\'", "|", "<", ">", "`"]
        for element in broken_list:
            if element in path:
                raise InvalidPathError(
                    f"Элемент {element} не может быть в пути"
                )

    def _path_exists(self, path: str) -> None:
        self._correct_path(path)
        if not os.path.exists(path):
            raise PathNotFoundError(
                f"Файл или директория не найдены: {path}"
            ) from None

    def _is_file(self, path: str):
        if not os.path.isfile(path):
            raise NotAFileError(f"Не является файлом: {path}") from None

    def _is_directory(self, path: str):
        if not os.path.isdir(path):
            raise NotADirectoryError(
                f"Не является директорией: {path}"
            ) from None

    def _is_tokens(self, tokens: argparse.Namespace):
        if not tokens.paths:
            message = "Отсутствует путь файла"
            logging.error(message)
            raise PathNotFoundError(message) from None
