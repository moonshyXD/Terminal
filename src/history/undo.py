import argparse
import os
import shutil

from src.file_commands.base_command import BaseClass


class Undo(BaseClass):
    def __init__(self):
        self.undo_path = os.path.join(os.getcwd(), "src/history/.trash")
        self.last_tokens: argparse.Namespace
        self.COMMANDS = {
            "cp": self._undo_cp,
            "mv": self._undo_mv,
            "rm": self._undo_rm,
        }

    def execute(self, tokens: argparse.Namespace):
        self.COMMANDS[self.last_tokens.command](self.last_tokens)

    def _undo_cp(self, tokens: argparse.Namespace):
        abs_from_path = tokens.paths[1]

        if os.path.isdir(abs_from_path):
            shutil.rmtree(abs_from_path)
        else:
            os.remove(abs_from_path)

    def _undo_mv(self, tokens: argparse.Namespace):
        abs_from_path = tokens.paths[1]
        abs_to_path = tokens.paths[0]

        print(abs_from_path, abs_to_path)

        shutil.move(abs_from_path, abs_to_path)

    def _undo_rm(self, tokens: argparse.Namespace):
        abs_from_path = os.path.join(self.undo_path, tokens.paths[0])
        abs_to_path = tokens.paths[1]

        print(abs_from_path, abs_to_path)
        shutil.move(abs_from_path, abs_to_path)
