import argparse
import os

from src.filesystem.base_command import BaseClass
from src.utils.errors import AlreadyExistsError, ShellError


class Mkdir(BaseClass):
    def execute(self, tokens: argparse.Namespace):
        try:
            self._is_tokens(tokens)
            for path in tokens.paths:
                abs_path = self._abs_path(path)

                self._already_exists(abs_path)
                os.mkdir(abs_path)
        except Exception as message:
            raise ShellError(message) from None

    def _already_exists(self, path: str):
        if os.path.exists(path):
            raise AlreadyExistsError("Эта директория уже создана")
