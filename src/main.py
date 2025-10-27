# src/main.py
import os
import shlex
import sys

from logger.logger import Logger
from parser.parser import Parser
from src.archive import tar, untar, unzip, zip
from src.errors import ShellError
from src.file_commands import cat, cd, cp, ls, mv, rm
from src.grep import grep
from src.history import history, undo


class Terminal:
    def __init__(self):
        self.cat = cat.Cat()
        self.cd = cd.Cd()
        self.cp = cp.Cp()
        self.ls = ls.Ls()
        self.rm = rm.Rm()
        self.mv = mv.Mv()
        self.history = history.History()
        self.undo = undo.Undo()
        self.zip = zip.Zip()
        self.unzip = unzip.Unzip()
        self.tar = tar.Tar()
        self.untar = untar.Untar()
        self.grep = grep.Grep()
        self.logger = Logger()
        self.parser = Parser()

        self.COMMANDS = {
            "cat": self.cat.execute,
            "cd": self.cd.execute,
            "cp": self.cp.execute,
            "ls": self.ls.execute,
            "rm": self.rm.execute,
            "mv": self.mv.execute,
            "history": self.history.execute,
            "undo": self.undo.execute,
            "zip": self.zip.execute,
            "unzip": self.unzip.execute,
            "tar": self.tar.execute,
            "untar": self.untar.execute,
            "grep": self.grep.execute,
        }

    def run(self):
        self.logger.setup_logging()
        self.undo.clear_undo_history()

        initial_directory = os.getcwd()
        print(f"Изначальная директория: {initial_directory}")

        for line in sys.stdin:
            if not line.strip():
                continue

            self.logger.start_execution(line.strip())
            try:
                tokens = self.parser.parse(shlex.split(line.strip()))
                if tokens.command in self.COMMANDS:
                    self.COMMANDS[tokens.command](tokens)
                else:
                    print(f"Неизвестная команда: {tokens.command}")

                self.history.add_history(line)

                if tokens.command in ["cp"]:
                    self.undo.add_undo_history(line)

                self.logger.success_execution(line.strip())
            except ShellError as message:
                print(message)
                self.logger.failure_execution(str(message))
                continue

        os.chdir(initial_directory)
        print(f"\nВернулись в: {os.getcwd()}")


if __name__ == "__main__":
    terminal = Terminal()
    terminal.run()
