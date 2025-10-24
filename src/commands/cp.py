import logging
import re
import shutil

from src.commands.base_command import BaseClass
from src.errors import ShellError


class Cp(BaseClass):
    def execute(self, path: list, directory: bool):
        try:
            abs_from_path = self._abs_path(path[0])
            abs_to_path = self._abs_path(path[1])

            self._path_exists(abs_from_path)
            self._path_exists(abs_to_path)

            self._start_execution(path)

            if directory:
                copied_directory = re.search(r"([^/]+)/?$", abs_from_path)
                shutil.copytree(
                    f"{abs_from_path}",
                    f"{abs_to_path}{copied_directory}",
                    dirs_exist_ok=True,
                )
            else:
                shutil.copy(f"{abs_from_path}", f"{abs_to_path}")

            self._success_execution(path)
        except Exception as message:
            self._failure_execution(path, str(message))
            raise ShellError(str(message)) from None

    def _start_execution(
        self,
        path: list,
    ) -> None:
        log = f"""
Выполнение команды {self.command}
[Путь откуда] {path[0]}
[Путь куда] {path[1]}
"""
        logging.info(log)

    def _success_execution(
        self,
        path: list,
    ) -> None:
        log = f"""
Команда {self.command} успешно выполнилась
[Путь откуда] {path[0]}
[Путь куда] {path[1]}
"""
        logging.info(log)

    def _failure_execution(self, path: list, message: str) -> None:
        log = f"""
Команда {self.command} не была выполнена
[Путь откуда] {path[0]}
[Путь куда] {path[1]}
[Сообщение] {message}
"""
        logging.info(log)
