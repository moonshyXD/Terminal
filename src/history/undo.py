import argparse
import os
import shutil
from collections import deque

from parser.setup import Parser
from src.file_commands.base_command import BaseClass


class Undo(BaseClass):
    def __init__(self):
        self.undo_history_path = os.path.join(
            os.getcwd(), "src/history/.undo_history"
        )
        self.undo_trash_path = os.path.join(os.getcwd(), "src/history/.trash")
        self.parser = Parser()
        self.COMMANDS = {
            "cp": self._undo_cp,
            "mv": self._undo_mv,
            "rm": self._undo_rm,
        }

    def execute(self, tokens: argparse.Namespace):
        last_tokens = self.parser.parse(
            self._get_last_command().strip().split()
        )
        self.COMMANDS[last_tokens.command](last_tokens)

    def _undo_cp(self, tokens: argparse.Namespace):
        abs_from_path = tokens.paths[1]

        if os.path.isdir(abs_from_path):
            shutil.rmtree(abs_from_path)
        else:
            os.remove(abs_from_path)

    def _undo_mv(self, tokens: argparse.Namespace):
        abs_from_path = tokens.paths[0]
        abs_to_path = tokens.paths[1]

        print(abs_from_path, abs_to_path)

        shutil.move(abs_from_path, abs_to_path)

    def _undo_rm(self, tokens: argparse.Namespace):
        abs_from_path = os.path.join(self.undo_trash_path, tokens.paths[0])
        abs_to_path = tokens.paths[1]

        print(abs_from_path, abs_to_path)
        shutil.move(abs_from_path, abs_to_path)

    def _get_last_command(self):
        with open(self.undo_history_path, "r", encoding="utf-8") as file:
            return "".join(deque(file, maxlen=1))

    def add_undo_history(self, command: str):
        with open(self.undo_history_path, "a", encoding="utf-8") as file:
            file.write(f"{command}")

    def clear_undo_history(self):
        with open(self.undo_history_path, "w") as _:
            pass

        shutil.rmtree(self.undo_trash_path)
        os.makedirs(self.undo_trash_path)
