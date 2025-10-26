import argparse
import logging
from pathlib import Path

from src.errors import PathNotFoundError, ShellError
from src.file_commands.base_command import BaseClass


class Cat(BaseClass):
    def execute(self, tokens: argparse.Namespace) -> None:
        if not tokens.paths:
            message = "Missing file operand"
            logging.error(message)
            raise PathNotFoundError(message) from None

        paths = tokens.paths

        try:
            self._start_execution(paths)

            for path in paths:
                print(f"{path}: ")
                abs_path = self._abs_path(path)

                self._path_exists(abs_path)
                self._is_file(abs_path)

                path_to_read = Path(abs_path)
                content = path_to_read.read_text(encoding="utf-8")
                print(content)
        except Exception as message:
            self._failure_execution(paths, str(message))
            raise ShellError(str(message)) from None
