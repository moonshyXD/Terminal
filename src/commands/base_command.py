import logging
import os
from abc import ABC, abstractmethod

from errors import NotADirectoryError, NotAFileError, PathNotFoundError


class BaseCommand(ABC):
    _command: str = ""

    def __init__(self):
        self._command = self.__class__.__name__.lower()

    @property
    def command(self) -> str:
        return self._command

    @abstractmethod
    def execute(self, path: str) -> None:
        pass

    def _abs_path(self, path: str) -> str:
        if path == "~":
            return os.path.expanduser("~")
        elif path == "..":
            return os.path.dirname(os.getcwd())

        if not os.path.isabs(path):
            return os.path.abspath(os.path.join(os.getcwd(), path))

        return path

    def _path_exists(self, path: str) -> None:
        if not os.path.exists(path):
            log = f"""
[Команда] {self.command}
[Статус] ОШИБКА
[Сообщение] не найден файл по пути: {path}
"""
            logging.error(log)
            raise PathNotFoundError(log)

    def _is_file(self, path: str):
        if not os.path.isfile(path):
            log = f"""
[Команда] {self.command}
[Статус] ОШИБКА
[Сообщение] файл {path} не является файлом
"""
            logging.error(log)
            return NotAFileError

    def _is_directory(self, path: str):
        if not os.path.isdir(path):
            log = f"""
[Команда] {self.command}
[Статус] ОШИБКА
[Сообщение] файл {path} не является директорией
"""
            logging.error(log)
            return NotADirectoryError

    def _start_execution(self, path: str) -> None:
        log = f"""
Выполнение команды {self.command}
[Путь] {path}
"""
        logging.info(log)

    def _success_execution(self, path: str) -> None:
        log = f"""
Команда {self.command} успешно выполнилась
[Путь] {path}
"""
        logging.info(log)

    def _failure_execution(self, path: str, message: str) -> None:
        log = f"""
Команда {self.command} не была выполнена
[Путь] {path}
[Сообщение] {message}
"""
        logging.info(log)
