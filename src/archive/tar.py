import argparse
import logging
import re
import tarfile

from src.errors import ShellError
from src.file_commands.base_command import (
    BaseClass,
    InvalidPathError,
    PathNotFoundError,
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
            archive_path = self._abs_path(paths[1])

            self._path_exists(folder_tar)
            self._is_directory(folder_tar)

            if not archive_path.endswith((".tar.gz", ".tgz")):
                archive_path += ".tar.gz"

            archive_name = paths[1].replace(".tar.gz", "").replace(".tgz", "")
            match = re.search(r"([^/]+)/?$", archive_name)
            if match is not None:
                archive_name = match.group(1)
            else:
                raise InvalidPathError(f"Неверный путь: {archive_name}")

            self._tar(folder_tar, archive_path, archive_name)

        except Exception as message:
            raise ShellError(str(message)) from None

    def _tar(
        self, folder_tar: str, archive_path: str, archive_name: str
    ) -> None:
        """
        Создаёт tar.gz архив
        :param folder_tar: Путь к директории для архивации
        :param archive_path: Путь к создаваемому архиву
        :param archive_name: Имя архива внутри tar
        """
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(folder_tar, arcname=archive_name)

    def _is_tokens(self, tokens: argparse.Namespace) -> None:
        """
        Проверяет наличие необходимых путей
        :param tokens: Аргументы команды (пути к файлам и директориям)
        :raises PathNotFoundError: Если пути отсутствуют
        """
        if not tokens.paths or len(tokens.paths) < 2:
            message = "Отсутствует путь файла"
            logging.error(message)
            raise PathNotFoundError(message) from None
