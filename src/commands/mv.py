from commands.base_command import BaseClass
from errors import ShellError


class Mv(BaseClass):
    def execute(self, path: str):
        try:
            abs_path = self._abs_path(path)

            self._path_exists(abs_path)
            self._is_file(abs_path)
            self._start_execution(abs_path)

            # выполнение

            self._success_execution(abs_path)
        except Exception as message:
            self._failure_execution(path, str(message))
            raise ShellError(str(message)) from None
