import argparse
import os
import shutil

from src.errors import DeletingError, ShellError
from src.file_commands.base_command import BaseClass


class Rm(BaseClass):
    """
    Класс для удаления файлов и директорий
    """

    def __init__(self) -> None:
        """
        Инициализация команды удаления с путями к корзине и истории отмены
        """
        self.trash_path = os.path.join(os.getcwd(), "src/history/.trash")
        self.undo_history_path = os.path.join(
            os.getcwd(), "src/history/.undo_history"
        )

    def execute(self, tokens: argparse.Namespace) -> None:
        """
        Удаляет файлы или директории с перемещением в корзину
        :param tokens: Аргументы команды (пути к файлам и директориям, флаги)
        :raises ShellError: При ошибке удаления
        """
        try:
            if not tokens.paths:
                paths = [os.path.expanduser("~")]
            else:
                paths = tokens.paths

            directory = tokens.recursive

            for path in paths:
                abs_path = self._abs_path(path)
                self._path_exists(abs_path)

                if directory:
                    self._is_directory(abs_path)
                    self._is_root(abs_path)
                    print(f"Вы уверены, что хотите удалить {path}? [y/n]")
                    accept = input()
                    if accept == "y":
                        filename = os.path.basename(abs_path)
                        shutil.move(
                            abs_path, os.path.join(self.trash_path, filename)
                        )

                        self._save_undo_info(filename, os.getcwd())
                    else:
                        print(f"Отмена удаления {path}...")
                        continue
                else:
                    self._is_file(abs_path)
                    filename = os.path.basename(abs_path)
                    shutil.move(
                        abs_path, os.path.join(self.trash_path, filename)
                    )

                    self._save_undo_info(filename, os.getcwd())

        except Exception as message:
            raise ShellError(str(message)) from None

    def _save_undo_info(self, filename: str, original_dir: str) -> None:
        """
        Сохраняет информацию об удалённых файлах для отмены операции
        :param filename: Имя удалённого файла
        :param original_dir: Исходная директория файла
        """
        undo_line = f"rm {filename} {original_dir}\n"

        with open(self.undo_history_path, "a", encoding="utf-8") as file:
            file.write(undo_line)

    def _is_root(self, path: str) -> None:
        """
        Проверяет, является ли путь корневой или родительской директорией
        :param path: Путь для проверки
        :raises DeletingError: Если путь является защищённой директорией
        """
        root_paths = [
            "/",
            "/root",
            "/home",
            "/usr",
            "/etc",
            "/var",
            "/sys",
            "/proc",
            "C:\\",
            "C:\\Windows",
            "C:\\Program Files",
        ]
        if (
            path in root_paths
            or path == os.path.expanduser("~")
            or path == os.getcwd()
            or path == os.path.dirname(os.getcwd())
        ):
            raise DeletingError("Невозможно удалить корневую директорию")

        parent_dir = os.path.normpath(path)
        target = os.path.normpath(os.getcwd())

        if not parent_dir.endswith(os.sep):
            parent_dir += os.sep

        if target.startswith(parent_dir):
            raise DeletingError("Невозможно удалить родительскую директорию")
