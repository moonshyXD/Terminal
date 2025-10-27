import argparse
from pathlib import Path

from src.errors import ShellError
from src.file_commands.base_command import BaseClass


class Cat(BaseClass):
    """
    Класс для вывода содержимого файлов
    """

    def execute(self, tokens: argparse.Namespace) -> None:
        """
        Выводит содержимое файлов в консоль
        :param tokens: Аргументы команды (пути к файлам)
        :raises ShellError: При ошибке чтения файла
        """
        try:
            self._is_tokens(tokens)

            paths = tokens.paths
            for path in paths:
                print(f"{path}: ")
                abs_path = self._abs_path(path)

                self._path_exists(abs_path)
                self._is_file(abs_path)

                path_to_read = Path(abs_path)
                content = path_to_read.read_text(encoding="utf-8")
                print(content)
        except Exception as message:
            raise ShellError(str(message)) from None
