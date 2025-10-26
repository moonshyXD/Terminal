import os
import sys

from logger import setup
from parser.setup import Parser
from src.archive import unzip, zip
from src.errors import ShellError
from src.file_commands import cat, cd, cp, ls, mv, rm
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
        }

    def run(self):
        setup.setup_logging()
        initial_dir = os.getcwd()
        print(f"Начальная директория: {initial_dir}")

        for line in sys.stdin:
            try:
                tokens = self.parser.parse(line.strip().split())
                if tokens.command in self.COMMANDS:
                    self.COMMANDS[tokens.command](tokens)
                else:
                    print(f"Неизвестная команда: {tokens.command}")

                self.history.add_history(line)

                if tokens.command in ["cp", "rm", "mv"]:
                    self.undo.last_tokens = tokens

            except ShellError as message:
                print(f"{message}")
                continue
            except Exception as e:
                print(f"Неожиданная ошибка: {e}")
                continue

        os.chdir(initial_dir)
        print(f"\nВернулись в: {os.getcwd()}")


if __name__ == "__main__":
    terminal = Terminal()
    terminal.run()
