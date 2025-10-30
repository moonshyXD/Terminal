import argparse
import os
import tarfile

from src.errors import ShellError
from src.filesystem.base_command import (
    BaseClass,
)


class Tar(BaseClass):
    """
    Класс для создания tar.gz архивов
    """

    def execute(self, tokens: argparse.Namespace) -> None:
        """
        Создаёт tar.gz архив из директории
        :param tokens: Аргументы команды (пути к файлам и директориям)
        :raises ShellError: При ошибке создания архива
        :raises InvalidPathError: Если путь содержит недопустимые символы
        """
        try:
            self._is_tokens(tokens)
            paths = tokens.paths

            folder_tar = self._abs_path(paths[0])

            if len(paths) < 2:
                archive_path = folder_tar + ".tar.gz"
            else:
                archive_path = self._abs_path(paths[1])

            self._path_exists(folder_tar)
            self._is_directory(folder_tar)

            if not archive_path.endswith((".tar.gz", ".tgz")):
                archive_path += ".tar.gz"

            archive_name = os.path.basename(folder_tar.rstrip("/"))

            self._tar(folder_tar, archive_path, archive_name)
        except Exception as message:
            raise ShellError(str(message)) from None

    def _tar(
        self, folder_tar: str, archive_path: str, archive_name: str
    ) -> None:
        """
        Создаёт tar.gz архив
        :param folder_tar: Абсолютный путь к директории для архивации
        :param archive_path: Абсолютный путь к создаваемому архиву
        :param archive_name: Имя архива внутри tar
        """
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(folder_tar, arcname=archive_name)
