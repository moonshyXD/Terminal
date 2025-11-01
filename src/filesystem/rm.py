import argparse
import os
import shutil

from src.filesystem.base_command import BaseClass
from src.utils.errors import DeletingError


class Rm(BaseClass):
    """
    Класс для удаления файлов и директорий
    """

    def __init__(self) -> None:
        """
        Инициализация команды удаления с путями к корзине и историей отмены
        """
        self._history_path = os.path.join(os.getcwd(), "src/history/.history")
        self._trash_path = os.path.join(os.getcwd(), "src/history/.trash")
        self._undo_history_path = os.path.join(
            os.getcwd(), "src/history/.undo_history"
        )

    def execute(self, tokens: argparse.Namespace) -> None:
        """
        Удаляет файлы или директории с перемещением в корзину
        :param tokens: Аргументы команды (пути к файлам и директориям, флаги)
        :raises ShellError: При ошибке удаления
        """
        paths = tokens.paths or [os.path.expanduser("~")]
        is_recursive = tokens.recursive

        for path in paths:
            abs_path = self._abs_path(path)
            self._path_exists(abs_path)
            self._is_system_paths(abs_path)

            if is_recursive:
                if not os.path.isdir(abs_path):
                    raise DeletingError(f"{path} не является директорией")
                print(f"Вы уверены, что хотите удалить {path}? [y/n] ")
                answer = input()
                if answer != "y":
                    print(f"Отмена удаления {path}...")
                    continue
            else:
                if not os.path.isfile(abs_path):
                    raise DeletingError(f"{path} не является файлом")

            trash_filename = self._move_to_trash(abs_path)
            self._save_undo_info(trash_filename, os.getcwd())

    def _move_to_trash(self, path: str) -> str:
        """
        Перемещает файл/директорию в корзину.
        Возвращает финальное имя в корзине.
        """
        os.makedirs(self._trash_path, exist_ok=True)

        filename = os.path.basename(path)
        trash_dest = os.path.join(self._trash_path, filename)

        counter = 1
        while os.path.exists(trash_dest):
            name, ext = os.path.splitext(filename)
            trash_dest = os.path.join(
                self._trash_path, f"{name}_{counter}{ext}"
            )
            counter += 1

        shutil.move(path, trash_dest)

        return os.path.basename(trash_dest)

    def _save_undo_info(self, filename: str, original_dir: str) -> None:
        """
        Перемещает файл или директорию в корзину с генерацией уникального имени
        :param path: Абсолютный путь к файлу или директории для удаления
        :return: Имя файла/директории в корзине
        :raises ShellError: При ошибке перемещения в корзину
        """
        undo_line = f"rm {filename} {original_dir}\n"

        with open(self._undo_history_path, "a", encoding="utf-8") as f:
            f.write(undo_line)

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

    def _is_system_paths(self, path: str):
        system_paths = [
            self._undo_history_path,
            self._history_path,
            self._trash_path,
        ]

        if path in system_paths:
            raise DeletingError("Нельзя удалить эти системные файлы")
