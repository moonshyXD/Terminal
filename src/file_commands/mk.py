import os
from pathlib import Path

from src.errors import AlreadyExistsError, ShellError
from src.file_commands.base_command import BaseClass


class Mk(BaseClass):
    def execute(self, tokens):
        try:
            self._is_tokens(tokens.paths)
            for path in tokens.paths:
                abs_path = self._abs_path(path)

                if os.isdir(abs_path):
                    os.mkdir(abs_path)
                elif os.isfile(abs_path):
                    Path(abs_path).touch()
        except Exception as message:
            raise ShellError(message) from None

    def _already_exists(self, path: str):
        if os.path.exists(path):
            raise AlreadyExistsError("Этот файл или директория уже созданы")
