import argparse
import os

from src.commands.base_command import BaseClass
from src.errors import ShellError


class Cd(BaseClass):
    def execute(self, tokens: argparse.Namespace):
        if not tokens.paths:
            paths = [os.path.expanduser("~")]
        else:
            paths = tokens.paths

        try:
            abs_path = self._abs_path(paths[0])

            self._start_execution(paths)
            self._path_exists(abs_path)
            self._is_directory(abs_path)

            os.chdir(abs_path)
            print(f"Текущая директория: {os.getcwd()}")
        except Exception as message:
            self._failure_execution(paths, str(message))
            raise ShellError(str(message)) from None
