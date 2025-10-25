import argparse
import logging
import os
import shutil

from src.commands.base_command import BaseClass
from src.errors import PathNotFoundError, ShellError


class Mv(BaseClass):
    def execute(self, tokens: argparse.Namespace):
        if not tokens.paths:
            message = "No such file or directory"
            logging.error(message)
            raise PathNotFoundError(message) from None

        paths = tokens.paths

        try:
            abs_from_path = self._abs_path(paths[0])
            abs_to_path = self._abs_path(paths[1])

            self._start_execution(paths)
            self._path_exists(abs_from_path)

            if os.path.exists(abs_to_path):
                os.rename(abs_from_path, abs_to_path)
            else:
                shutil.move(abs_from_path, abs_to_path)

        except Exception as message:
            self._failure_execution(paths, str(message))
            raise ShellError(str(message)) from None
