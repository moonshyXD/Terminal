import argparse
import os
import tarfile

from src.filesystem.base_command import BaseClass


class Untar(BaseClass):
    """
    Класс для распаковки tar.gz архивов
    """

    def execute(self, tokens: argparse.Namespace) -> None:
        """
        Распаковывает tar.gz архив в текущую директорию
        :param tokens: Аргументы команды (путь к архиву)
        :raises ShellError: При ошибке распаковки архива
        """
        self._is_tokens(tokens)
        paths = tokens.paths

        archive_path = self._abs_path(paths[0])
        untar_to = os.getcwd()

        self._path_exists(archive_path)
        self._is_file(archive_path)

        self._untar(archive_path, untar_to)

    def _untar(self, archive_path: str, untar_to: str) -> None:
        """
        Распаковывает tar.gz архив
        :param archive_path: Путь к архиву
        :param untar_to: Директория для распаковки
        """
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(untar_to)
