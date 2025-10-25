import argparse
import logging
import os
import re
import shutil

from src.commands.base_command import BaseClass
from src.errors import ShellError


class Cp(BaseClass):
    def execute(self, tokens: argparse.Namespace):
        if not tokens.paths or len(tokens.paths) < 2:
            message = "Missing file operand"
            logging.error(message)
            raise ShellError(message) from None

        paths = tokens.paths
        directory = tokens.r

        try:
            abs_from_path = self._abs_path(paths[0])
            abs_to_path = self._abs_path(paths[1])

            self._start_execution(paths)
            self._path_exists(abs_from_path)

            if directory:
                self._is_directory(abs_from_path)
                self._path_exists(abs_to_path)

                match = re.search(r"([^/]+)/?$", abs_from_path)
                if match is not None:
                    copied_directory = match.group(1)
                    print(copied_directory)
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
            self._failure_execution(paths, str(message))
            raise ShellError(str(message)) from None

    def _start_execution(self, path: list) -> None:
        command_str = f"{self.command} {path[0]} {path[1]}"
        logging.info(command_str)
