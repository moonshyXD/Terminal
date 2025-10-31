import argparse
import os

from src.filesystem.base_command import BaseClass
from src.utils.errors import ShellError


class Cd(BaseClass):
    """
    Класс для изменения текущей директории
    """

    def execute(self, tokens: argparse.Namespace) -> None:
        """
        Изменяет текущую рабочую директорию
        :param tokens: Аргументы команды (пути к директориям)
        :raises ShellError: При ошибке смены директории
        """
        try:
            if not tokens.paths:
                paths = [os.path.expanduser("~")]
            else:
                paths = tokens.paths

            abs_path = self._abs_path(paths[0])

            self._path_exists(abs_path)
            self._is_directory(abs_path)

            os.chdir(abs_path)
        except Exception as message:
            raise ShellError(str(message)) from None
