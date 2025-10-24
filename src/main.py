import os
import sys

from logger import setup
from parser.setup import Parser
from src.commands import cat, cd, cp, ls


class Terminal:
    def __init__(self):
        self.cat = cat.Cat()
        self.cd = cd.Cd()
        self.cp = cp.Cp()
        self.ls = ls.Ls()
        self.parser = Parser()

    def run(self):
        setup.setup_logging()
        initial_dir = os.getcwd()
        print(f"Начальная директория: {initial_dir}")

        for line in sys.stdin:
            tokens = self.parser.parse(line.strip().split())
            if tokens:
                print(tokens)

        os.chdir(initial_dir)
        print(f"\nВернулись в: {os.getcwd()}")


if __name__ == "__main__":
    terminal = Terminal()
    terminal.run()
