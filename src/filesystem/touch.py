from pathlib import Path

from src.filesystem.base_command import BaseClass


class Touch(BaseClass):
    def execute(self, tokens):
        self._is_tokens(tokens)
        for path in tokens.paths:
            abs_path = self._abs_path(path)

            Path(abs_path).touch()
