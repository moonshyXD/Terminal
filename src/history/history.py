import argparse
import os
from collections import deque

from src.errors import ShellError
from src.file_commands.base_command import BaseClass


class History(BaseClass):
    """
    Класс для управления историей выполненных команд
    """
    def __init__(self) -> None:
        """
        Инициализация истории команд с путём к файлу истории
        """
        self.history_path = os.path.join(os.getcwd(), "src/history/.history")

    def execute(self, tokens: argparse.Namespace) -> None:
        """
        Выводит историю последних выполненных команд
        :param tokens: Аргументы команды (количество команд для отображения)
        :raises ShellError: При ошибке чтения файла истории
        """
        try:
            count_commands = tokens.count
            history = self._get_history(count_commands)
            for line in history:
                print(line, end="")
        except Exception as message:
            raise ShellError(str(message)) from None

    def _get_history(self, count_commands: int) -> deque[str]:
        """
        Получает последние count_commands команд из файла истории
        :param count_commands: Количество команд для получения
        :return: Список последних команд в виде deque
        """
        with open(self.history_path, "r", encoding="utf-8") as file:
            return deque(file, maxlen=count_commands)

    def _get_line_number(self) -> str:
        """
        Получает номер последней строки в истории
        :return: Номер последней строки в виде строки
        """
        history = "".join(self._get_history(count_commands=1))
        return history.split()[0]

    def add_history(self, command: str) -> None:
        """
        Добавляет новую команду в историю
        :param command: Команда для добавления в историю
        """
        line_number = int(self._get_line_number())
        with open(self.history_path, "a", encoding="utf-8") as file:
            file.write(f"{line_number + 1} {command}")
