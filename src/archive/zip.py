import argparse
import os
import zipfile

from src.errors import ShellError
from src.file_commands.base_command import BaseClass


class Zip(BaseClass):
    """
    Класс для создания zip архивов
    """

    def execute(self, tokens: argparse.Namespace) -> None:
        """
        Создаёт zip архив из директории
        :param tokens: Аргументы команды (пути к файлу или директории)
        :raises ShellError: При ошибке создания архива
        """
        try:
            self._is_tokens(tokens)
            paths = tokens.paths

            folder_zip = self._abs_path(paths[0])

            if len(paths) < 2:
                archive_path = folder_zip + ".zip"
            else:
                archive_path = self._abs_path(paths[1])

            self._path_exists(folder_zip)
            self._is_directory(folder_zip)

            if not archive_path.endswith(".zip"):
                archive_path += ".zip"

            self._zip(folder_zip, archive_path)
        except Exception as message:
            raise ShellError(str(message)) from None

    def _zip(self, folder_zip: str, archive_path: str) -> None:
        """
        Создаёт zip архив
        :param folder_zip: Абсолютный путь к директории для архивации
        :param archive_path: Абсолютный путь к создаваемому архиву
        """
        with zipfile.ZipFile(
            archive_path, "w", zipfile.ZIP_DEFLATED
        ) as zip_file:
            for root, _, files in os.walk(folder_zip):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_zip)
                    zip_file.write(file_path, arcname)
