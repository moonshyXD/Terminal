import argparse
import os
import shutil
from collections import deque

from parser.parser import Parser
from src.errors import PathNotFoundError, ShellError, UndoError
from src.file_commands.base_command import BaseClass


class Undo(BaseClass):
    def __init__(self):
        self._command = self.__class__.__name__.lower()
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
        try:
            last_commands = self._get_last_command_group()

            if not last_commands:
                last_cmd = self._get_last_command()
                if not last_cmd:
                    raise UndoError("Команды для отмены не найдены")
                last_commands = [last_cmd]

            for cmd in last_commands:
                parsed_tokens = self.parser.parse(cmd.strip().split())
                if parsed_tokens.command in self.COMMANDS:
                    self.COMMANDS[parsed_tokens.command](parsed_tokens)

            self._remove_last_lines(len(last_commands))
        except Exception as message:
            raise ShellError(str(message)) from None

    def _get_last_command_group(self):
        try:
            with open(self.undo_history_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            if not lines:
                return []

            last_cmd = (
                lines[-1].strip().split()[0] if lines[-1].strip() else ""
            )

            if last_cmd in ["mv", "rm"]:
                result = []
                for line in reversed(lines):
                    cmd = line.strip().split()[0] if line.strip() else ""
                    if cmd == last_cmd:
                        result.insert(0, line)
                    else:
                        break
                return result

            return []
        except FileNotFoundError:
            raise PathNotFoundError("Файл не найден") from None

    def _remove_last_lines(self, count: int):
        try:
            with open(self.undo_history_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            remaining = lines[:-count] if count < len(lines) else []

            with open(self.undo_history_path, "w", encoding="utf-8") as file:
                file.writelines(remaining)
        except FileNotFoundError:
            raise PathNotFoundError("Файл не найден") from None

    def _undo_cp(self, tokens: argparse.Namespace):
        abs_from_path = tokens.paths[1]

        if os.path.isdir(abs_from_path):
            shutil.rmtree(abs_from_path)
        else:
            os.remove(abs_from_path)

    def _undo_mv(self, tokens: argparse.Namespace):
        abs_from_path = tokens.paths[0]
        abs_to_path = tokens.paths[1]

        shutil.move(abs_from_path, abs_to_path)

    def _undo_rm(self, tokens: argparse.Namespace):
        filename = tokens.paths[0]
        restore_dir = tokens.paths[1]

        abs_from_path = os.path.join(self.undo_trash_path, filename)
        abs_to_path = os.path.join(restore_dir, filename)

        shutil.move(abs_from_path, abs_to_path)

    def _get_last_command(self):
        try:
            with open(self.undo_history_path, "r", encoding="utf-8") as file:
                return "".join(deque(file, maxlen=1))
        except FileNotFoundError:
            return ""

    def add_undo_history(self, command: str):
        with open(self.undo_history_path, "a", encoding="utf-8") as file:
            file.write(f"{command}")

    def clear_undo_history(self):
        with open(self.undo_history_path, "w") as _:
            pass
        shutil.rmtree(self.undo_trash_path)
        os.makedirs(self.undo_trash_path)
