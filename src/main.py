import os
import sys

from logger import setup
from parser.setup import Parser
from src.commands import cat, cd, cp, ls, rm
from src.errors import ShellError


class Terminal:
    def __init__(self):
        self.cat = cat.Cat()
        self.cd = cd.Cd()
        self.cp = cp.Cp()
        self.ls = ls.Ls()
        self.rm = rm.Rm()
        self.parser = Parser()

        self.COMMANDS = {
            "cat": self.cat.execute,
            "cd": self.cd.execute,
            "cp": self.cp.execute,
            "ls": self.ls.execute,
            "rm": self.rm.execute
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
            except ShellError as message:
                print(f"{message}")
                continue
            except KeyboardInterrupt:
                print("\nВыход...")
                break
            except EOFError:
                break
            except Exception as e:
                print(f"Неожиданная ошибка: {e}")
                continue

        os.chdir(initial_dir)
        print(f"\nВернулись в: {os.getcwd()}")


if __name__ == "__main__":
    terminal = Terminal()
    terminal.run()
