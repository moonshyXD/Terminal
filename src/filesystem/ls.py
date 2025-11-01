import argparse
import os
import stat
from datetime import datetime

from src.filesystem.base_command import BaseClass


class Ls(BaseClass):
    """
    Класс для отображения содержимого директорий
    """

    def execute(self, tokens: argparse.Namespace) -> None:
        """
        Выводит список файлов и директорий
        :param tokens: Аргументы команды (пути к директориям)
        :raises ShellError: При ошибке чтения директории
        """
        if tokens.paths:
            paths = tokens.paths
        else:
            paths = [os.getcwd()]

        detailed = tokens.l or tokens.al
        all_files = tokens.all or tokens.al

        for path in paths:
            abs_path = self._abs_path(path)

            self._path_exists(abs_path)
            self._is_directory(abs_path)

            items = os.listdir(abs_path)

            print(f"{path}:")
            if detailed:
                self._print_detailed(items, abs_path, all_files)
            else:
                self._print_not_detailed(items, abs_path, all_files)

            print()

    def _print_detailed(
        self, items: list, abs_path: str, all_files: bool
    ) -> None:
        """
        Выводит подробную информацию о файлах
        :param items: Список элементов директории
        :param abs_path: Абсолютный путь к директории
        :param all_files: Показать скрытые файлы
        """
        for item in sorted(items):
            item_path = os.path.join(abs_path, item)

            stats = os.stat(item_path)

            mode = stat.filemode(stats.st_mode)
            item_size = stats.st_size

            mtime = datetime.fromtimestamp(stats.st_mtime)
            mtime_str = mtime.strftime("%Y-%m-%d %H:%M")

            if item[0] != "." or all_files:
                if os.path.isdir(item_path):
                    colored_name = f"\033[34;42m{item}\033[0m"
                    log = f"{mode} {item_size:>10} {mtime_str} {colored_name}"
                else:
                    colored_name = f"\033[32m{item}\033[0m"
                    log = f"{mode} {item_size:>10} {mtime_str} {colored_name}"

                print(log)

    def _print_not_detailed(
        self, items: list, abs_path: str, all_files: bool
    ) -> None:
        """
        Выводит список файлов
        :param items: Список элементов директории
        :param abs_path: Абсолютный путь к директории
        :param all_files: Показать скрытые файлы
        """
        for item in sorted(items):
            if item[0] != "." or all_files:
                item_path = os.path.join(abs_path, item)
                if os.path.isdir(item_path):
                    print(f"\033[34;42m{item}\033[0m", end=" ")
                else:
                    print(f"\033[32m{item}\033[0m", end=" ")
