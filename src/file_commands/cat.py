import argparse
import logging
from pathlib import Path

from src.errors import NotTextFile, PathNotFoundError, ShellError
from src.file_commands.base_command import BaseClass


class Cat(BaseClass):
    def execute(self, tokens: argparse.Namespace) -> None:
        if not tokens.paths:
            message = "Missing file operand"
            logging.error(message)
            raise PathNotFoundError(message) from None

        paths = tokens.paths

        try:
            abs_path = self._abs_path(paths[0])

            self._start_execution(paths)
            self._path_exists(abs_path)
            self._is_file(abs_path)
            self._is_text_file(abs_path)

            path_to_read = Path(abs_path)
            content = path_to_read.read_text(encoding="utf-8")
            print(content)
        except Exception as message:
            self._failure_execution(paths, str(message))
            raise ShellError(str(message)) from None

    def _is_text_file(self, path: str) -> None:
        text_extensions = {".txt", ".py", ".json", ".xml", ".md"}
        file_extension = Path(path).suffix.lower()
        if file_extension not in text_extensions:
            message = f"Not a text file: {file_extension}"
            logging.error(message)
            raise NotTextFile(message) from None
