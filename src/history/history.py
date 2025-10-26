import argparse
import os
from collections import deque

from src.file_commands.base_command import BaseClass


class History(BaseClass):
    def __init__(self):
        self._command = self.__class__.__name__.lower()
        self.history_path = os.path.join(os.getcwd(), "src/history/.history")

    def execute(self, tokens: argparse.Namespace):
        self._start_execution(tokens.paths)
        count_commands = tokens.count
        history = self._get_history(count_commands)
        for line in history:
            print(line, end="")

    def _get_history(self, count_commands: int):
        with open(self.history_path, "r", encoding="utf-8") as file:
            return deque(file, maxlen=count_commands)

    def _get_line_number(self):
        history = "".join(self._get_history(count_commands=1))
        return history.split()[0]

    def add_history(self, command: str):
        line_number = int(self._get_line_number())
        with open(self.history_path, "a", encoding="utf-8") as file:
            file.write(f"{line_number + 1} {command}")
