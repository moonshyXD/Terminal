import argparse
import logging
import os
import re
import shutil

from src.errors import PathNotFoundError, ShellError
from src.file_commands.base_command import BaseClass


class Cp(BaseClass):
    """
    Класс для копирования файлов и директорий
    """

    def __init__(self) -> None:
        """
        Инициализация команды копирования с путём истории отмены
        """
        self._command = self.__class__.__name__.lower()
        self.undo_history_path = os.path.join(
            os.getcwd(), "src/history/.undo_history"
        )

    def execute(self, tokens: argparse.Namespace) -> None:
        """
        Копирует файлы или директории
        :param tokens: Аргументы команды (пути к файлам и директория, флаги)
        :raises ShellError: При ошибке копирования
        :raises PathNotFoundError: Если пути отсутствуют
        """
        try:
            self._is_tokens(tokens)

            paths = tokens.paths
            directory = tokens.recursive

            abs_from_path = self._abs_path(paths[0])
            abs_to_path = self._abs_path(paths[1])

            self._path_exists(abs_from_path)

            if directory:
                self._is_directory(abs_from_path)
                self._path_exists(abs_to_path)

                match = re.search(r"([^/]+)/?$", abs_from_path)
                if match is not None:
                    copied_directory = match.group(1)
                else:
                    raise ShellError(f"Неверный путь: {abs_from_path}")

                target_path = os.path.join(abs_to_path, copied_directory)

                shutil.copytree(
                    abs_from_path,
                    target_path,
                    dirs_exist_ok=True,
                )

                self._save_undo_info(target_path)
            else:
                directory_path = os.path.dirname(abs_to_path)
                self._path_exists(directory_path)
                self._is_file(abs_from_path)

                shutil.copy(abs_from_path, abs_to_path)

                self._save_undo_info(abs_to_path)

        except Exception as message:
            raise ShellError(str(message)) from None

    def _save_undo_info(self, copied_path: str) -> None:
        """
        Сохраняет информацию о скопированном файле для отмены
        :param copied_path: Абсолютный путь к скопированному файлу/директории
        """
        undo_line = f"cp {copied_path}\n"

        with open(self.undo_history_path, "a", encoding="utf-8") as file:
            file.write(undo_line)

    def _is_tokens(self, tokens: argparse.Namespace) -> None:
        """
        Проверяет наличие необходимых путей
        :param tokens: Аргументы команды
        :raises PathNotFoundError: Если пути отсутствуют
        """
        if not tokens.paths or len(tokens.paths) < 2:
            message = "Отсутствует путь файла"
            logging.error(message)
            raise PathNotFoundError(message) from None
