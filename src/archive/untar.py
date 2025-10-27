import argparse
import os
import tarfile

from src.errors import ShellError
from src.file_commands.base_command import BaseClass


class Untar(BaseClass):
    def execute(self, tokens: argparse.Namespace):
        try:
            self._is_tokens(tokens)
            paths = tokens.paths

            archive_path = self._abs_path(paths[0])
            untar_to = os.getcwd()

            self._path_exists(archive_path)
            self._is_file(archive_path)

            self._untar(archive_path, untar_to)

        except Exception as message:
            raise ShellError(str(message)) from None

    def _untar(self, archive_path: str, untar_to: str):
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(untar_to)
