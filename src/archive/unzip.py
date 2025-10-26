import argparse
import logging
import os
import re
import zipfile

from src.errors import ShellError
from src.file_commands.base_command import BaseClass


class Unzip(BaseClass):
    def execute(self, tokens: argparse.Namespace):
        self._start_execution(tokens.paths)

        if not tokens.paths:
            message = "Missing file operand"
            logging.error(message)
            raise ShellError(message) from None

        paths = tokens.paths
        try:
            archive_path = self._abs_path(paths[0])
            unzip_to = os.path.join(
                os.getcwd(), re.sub(r"\.zip$", "", paths[0])
            )

            self._path_exists(archive_path)
            self._is_file(archive_path)

            self._unzip(archive_path, unzip_to)
        except Exception as message:
            self._failure_execution(paths, str(message))
            raise ShellError(str(message)) from None

    def _unzip(self, archive_path: str, unzip_to: str):
        os.mkdir(unzip_to)
        with zipfile.ZipFile(archive_path, "r") as zip_file:
            zip_file.extractall(unzip_to)
