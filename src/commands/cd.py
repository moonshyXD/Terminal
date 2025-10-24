import os

from src.commands.base_command import BaseClass
from src.errors import ShellError


class Cd(BaseClass):
    def execute(self, path: list):
        try:
            abs_path = self._abs_path(path[0])

            self._path_exists(abs_path)
            self._is_directory(abs_path)
            self._start_execution(path[0])

            os.chdir(abs_path)

            self._success_execution(path[0])
        except Exception as message:
            self._failure_execution(path[0], str(message))
            raise ShellError(str(message)) from None
