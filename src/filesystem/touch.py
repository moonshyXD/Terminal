import os
from pathlib import Path

from src.errors import AlreadyExistsError, ShellError
from src.filesystem.base_command import BaseClass


class Touch(BaseClass):
    def execute(self, tokens):
        try:
            self._is_tokens(tokens)
            for path in tokens.paths:
                abs_path = self._abs_path(path)

                self._already_exists(abs_path)
                Path(abs_path).touch()
        except Exception as message:
            raise ShellError(message) from None

    def _already_exists(self, path: str):
        if os.path.exists(path):
            raise AlreadyExistsError("Этот файл уже создан")
