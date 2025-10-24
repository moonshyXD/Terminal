import logging
import re
import shutil

from commands.base_command import BaseClass
from errors import ShellError


class Cp(BaseClass):
    def execute(self, from_path: str, to_path: str, directory: bool):
        try:
            abs_from_path = self._abs_path(from_path)
            abs_to_path = self._abs_path(to_path)

            self._path_exists(abs_from_path)
            self._path_exists(abs_to_path)

            self._start_execution(abs_from_path, abs_to_path)

            if directory:
                copied_directory = re.search(r"([^/]+)/?$", abs_from_path)
                shutil.copytree(
                    f"{abs_from_path}",
                    f"{abs_to_path}{copied_directory}",
                    dirs_exist_ok=True,
                )
            else:
                shutil.copy(f"{abs_from_path}", f"{abs_to_path}")

            self._success_execution(abs_from_path, abs_to_path)
        except Exception as message:
            self._failure_execution(abs_from_path, abs_to_path, str(message))
            raise ShellError(str(message)) from None

    def _start_execution(self, from_path: str, to_path: str) -> None:
        log = f"""
Выполнение команды {self.command}
[Путь откуда] {from_path}
[Путь куда] {to_path}
"""
        logging.info(log)

    def _success_execution(self, from_path: str, to_path: str) -> None:
        log = f"""
Команда {self.command} успешно выполнилась
[Путь откуда] {from_path}
[Путь куда] {to_path}
"""
        logging.info(log)

    def _failure_execution(
        self, from_path: str, to_path: str, message: str
    ) -> None:
        log = f"""
Команда {self.command} не была выполнена
[Путь откуда] {from_path}
[Путь куда] {to_path}
[Сообщение] {message}
"""
        logging.info(log)
