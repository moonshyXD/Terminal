import argparse
import logging
import os
from abc import ABC, abstractmethod

from src.utils.errors import (
    InvalidPathError,
    NotADirectoryError,
    NotAFileError,
    PathNotFoundError,
)


class BaseClass(ABC):
    """
    Базовый класс для всех команд
    """

    @abstractmethod
    def execute(self, tokens: argparse.Namespace) -> None:
        """
        Абстрактный метод для выполнения команды
        :param tokens: Аргументы команды
        """
        pass

    def _abs_path(self, path: str) -> str:
        """
        Преобразует путь в абсолютный
        :param path: Относительный или абсолютный путь
        :return: Абсолютный путь
        """
        if path == "~":
            return os.path.expanduser("~")
        elif path == "..":
            return os.path.dirname(os.getcwd())

        if not os.path.isabs(path):
            return os.path.join(os.getcwd(), path)

        return path

    def _correct_path(self, path: str) -> None:
        """
        Проверяет путь на наличие недопустимых символов
        :param path: Путь для проверки
        :raises InvalidPathError: Если путь содержит недопустимые символы
        """
        broken_list = ["#", "&", "(", ")", "*", "?", "''", "|", "<", ">", "`"]
        for element in broken_list:
            if element in path:
                raise InvalidPathError(
                    f"Элемент {element} не может быть в пути"
                )

    def _path_exists(self, path: str) -> None:
        """
        Проверяет существование пути
        :param path: Путь для проверки
        :raises PathNotFoundError: Если путь не существует
        """
        self._correct_path(path)
        if not os.path.exists(path):
            raise PathNotFoundError(
                f"Файл или директория не найдены: {path}"
            ) from None

    def _is_file(self, path: str) -> None:
        """
        Проверяет, является ли путь файлом
        :param path: Путь для проверки
        :raises NotAFileError: Если путь не является файлом
        """
        if not os.path.isfile(path):
            raise NotAFileError(f"Не является файлом: {path}") from None

    def _is_directory(self, path: str) -> None:
        """
        Проверяет, является ли путь директорией
        :param path: Путь для проверки
        :raises NotADirectoryError: Если путь не является директорией
        """
        if not os.path.isdir(path):
            raise NotADirectoryError(
                f"Не является директорией: {path}"
            ) from None

    def _is_tokens(self, tokens: argparse.Namespace) -> None:
        """
        Проверяет наличие путей в аргументах
        :param tokens: Аргументы команды
        :raises PathNotFoundError: Если пути отсутствуют
        """
        if not tokens.paths:
            message = "Отсутствует путь файла"
            logging.error(message)
            raise PathNotFoundError(message) from None
