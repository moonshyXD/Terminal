import argparse
import logging
import os
import zipfile

from src.errors import ShellError
from src.file_commands.base_command import BaseClass


class Zip(BaseClass):
    def execute(self, tokens: argparse.Namespace):
        self._start_execution(tokens.paths)

        if not tokens.paths or len(tokens.paths) < 2:
            message = "Missing file operand"
            logging.error(message)
            raise ShellError(message) from None

        paths = tokens.paths

        try:
            folder_zip = self._abs_path(paths[0])
            archive_path = self._abs_path(paths[1])

            self._path_exists(folder_zip)
            self._is_directory(folder_zip)

            if not archive_path.endswith(".zip"):
                archive_path += ".zip"

            self._zip(folder_zip, archive_path)
        except Exception as message:
            self._failure_execution(paths, str(message))
            raise ShellError(str(message)) from None

    def _zip(self, folder_zip: str, archive_path: str):
        with zipfile.ZipFile(
            archive_path, "w", zipfile.ZIP_DEFLATED
        ) as zip_file:
            for root, _, files in os.walk(folder_zip):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_zip)
                    zip_file.write(file_path, arcname)
