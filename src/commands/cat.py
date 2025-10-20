import logging
from pathlib import Path

from commands.base_command import BaseClass
from errors import NotTextFile, ShellError


class Cat(BaseClass):
    def execute(self, path: str) -> None:
        try:
            abs_path = self._abs_path(path)

            self._path_exists(abs_path)
            self._is_file(abs_path)
            self._start_execution(abs_path)
            self._is_text_file(abs_path)

            abs_path = Path(abs_path)
            content = abs_path.read_text(encoding="utf-8")
            print(content)

            self._success_execution(abs_path)
        except Exception as message:
            self._failure_execution(path, str(message))
            raise ShellError(str(message)) from None

    def _is_text_file(self, path: str) -> None:
        text_extensions = {".txt", ".py", ".json", ".xml"}
        file_extension = Path(path).suffix.lower()
        if file_extension not in text_extensions:
            log = f"""
[Команда] {self.command}
[Статус] ОШИБКА
[Сообщение] файл {file_extension} не является текстовым
"""
            logging.error(log)
            raise NotTextFile
