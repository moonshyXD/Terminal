import os

from commands.base_command import BaseClass
from errors import ShellError


class Cd(BaseClass):
    def execute(self, path: str):
        try:
            abs_path = self._abs_path(path)

            self._path_exists(abs_path)
            self._is_directory(abs_path)
            self._start_execution(abs_path)

            os.chdir(abs_path)

            self._success_execution(abs_path)
        except Exception as message:
            self._failure_execution(path, str(message))
            raise ShellError(str(message)) from None
