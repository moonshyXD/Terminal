import argparse
import logging
import os
import shutil

from src.errors import MovingError, PathNotFoundError, ShellError
from src.file_commands.base_command import BaseClass


class Mv(BaseClass):
    def execute(self, tokens: argparse.Namespace):
        if not tokens.paths or len(tokens.paths) < 2:
            message = "Missing file operand"
            logging.error(message)
            raise PathNotFoundError(message)

        paths = tokens.paths

        try:
            abs_from_path = self._abs_path(paths[0])
            abs_to_path = self._abs_path(paths[1])

            self._start_execution(paths)

            self._path_exists(abs_from_path)

            if not os.access(abs_from_path, os.R_OK):
                message = f"Cannot access '{paths[0]}': Permission denied"
                logging.error(message)
                raise MovingError(message)

            target_dir = os.path.dirname(abs_to_path) or "."
            if not os.access(target_dir, os.W_OK):
                message = f"Cannot move to '{paths[1]}': Permission denied"
                logging.error(message)
                raise MovingError(message)

            shutil.move(abs_from_path, abs_to_path)

        except Exception as message:
            self._failure_execution(paths, str(message))
            raise ShellError(str(message)) from None
