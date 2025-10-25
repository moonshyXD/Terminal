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
            raise ShellError(message)

        paths = tokens.paths
        directory = tokens.r

        try:
            abs_from_path = self._abs_path(paths[0])
            abs_to_path = self._abs_path(paths[1])

            self._start_execution(paths)
            self._path_exists(abs_from_path)

            if directory:
                copied_directory = re.search(r"([^/]+)/?$", abs_from_path)

                if copied_directory is None:
                    raise ShellError(f"Invalid path: {abs_from_path}")

                dir_name = copied_directory.group(1)
                target_path = os.path.join(abs_to_path, dir_name)

                shutil.copytree(
                    abs_from_path,
                    target_path,
                    dirs_exist_ok=True,
                )
            else:
                if os.path.isdir(abs_to_path):
                    shutil.copy(abs_from_path, abs_to_path)
                else:
                    shutil.copy(abs_from_path, abs_to_path)

        except Exception as message:
            self._failure_execution(paths, str(message))
            raise ShellError(str(message)) from None

    def _start_execution(self, path: list) -> None:
        command_str = f"{self.command} {path[0]} {path[1]}"
        logging.info(command_str)
