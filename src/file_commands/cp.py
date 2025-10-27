import argparse
import logging
import os
import re
import shutil

from src.errors import PathNotFoundError, ShellError
from src.file_commands.base_command import BaseClass


class Cp(BaseClass):
    def execute(self, tokens: argparse.Namespace):
        try:
            self._is_tokens(tokens)

            paths = tokens.paths
            directory = tokens.recursive

            abs_from_path = self._abs_path(paths[0])
            abs_to_path = self._abs_path(paths[1])

            self._path_exists(abs_from_path)

            if directory:
                self._is_directory(abs_from_path)
                self._path_exists(abs_to_path)

                match = re.search(r"([^/]+)/?$", abs_from_path)
                if match is not None:
                    copied_directory = match.group(1)
                else:
                    raise ShellError(f"Invalid path: {abs_from_path}")

                target_path = os.path.join(abs_to_path, copied_directory)

                shutil.copytree(
                    abs_from_path,
                    target_path,
                    dirs_exist_ok=True,
                )
            else:
                directory_path = os.path.dirname(abs_to_path)
                self._path_exists(directory_path)
                self._is_file(abs_from_path)
                shutil.copy(abs_from_path, abs_to_path)

        except Exception as message:
            raise ShellError(str(message)) from None

    def _is_tokens(self, tokens: argparse.Namespace):
        if not tokens.paths or len(tokens.paths) < 2:
            message = "Missing file operand"
            logging.error(message)
            raise PathNotFoundError(message) from None
