# src/main.py
import os
import shlex
import sys

from logger.logger import Logger
from parser.parser import Parser
from src.archive import tar, untar, unzip, zip
from src.errors import ShellError
from src.file_commands import cat, cd, cp, ls, mkdir, mv, rm, touch
from src.grep import grep
from src.history import history, undo


class Terminal:
    """
    Основной класс терминала для управления командами
    """

    def __init__(self) -> None:
        """
        Инициализация терминала с загрузкой всех команд
        """
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
        self.mkdir = mkdir.Mkdir()
        self.touch = touch.Touch()
        self.logger = Logger()
        self.parser = Parser()

        self.COMMANDS = {
            name: getattr(self, name).execute
            for name in [
                "cat",
                "cd",
                "cp",
                "ls",
                "rm",
                "mv",
                "history",
                "undo",
                "zip",
                "unzip",
                "tar",
                "untar",
                "grep",
                "touch",
                "mkdir",
            ]
        }

    def run(self) -> None:
        """
        Запуск терминала.
        Читает команды из stdin и выполняет их
        :raises ShellError: При ошибке выполнения команды
        """
        self.logger.setup_logging()
        self.undo.clear_undo_history()

        print("Приветствуем вас в мини-оболочке с файловыми командами.")
        print("Для помощи в работе с командами пропишите в консоли --help")

        print(f"> {os.getcwd()} ", end="", flush=True)

        for line in sys.stdin:
            if not line.strip():
                print(f"> {os.getcwd()} ", end="", flush=True)
                continue

            self.logger.start_execution(line.strip())
            try:
                tokens = self.parser.parse(shlex.split(line.strip()))
                if tokens is None:
                    print(f"> {os.getcwd()} ", end="", flush=True)
                    continue

                if tokens.command == "stop":
                    break

                if tokens.command in self.COMMANDS:
                    self.COMMANDS[tokens.command](tokens)
                else:
                    print(f"Неизвестная команда: {tokens.command}")

                self.history.add_history(line)

                self.logger.success_execution(line.strip())
            except ShellError as message:
                print(message)
                self.logger.failure_execution(str(message))

            print(f"> {os.getcwd()} ", end="", flush=True)


if __name__ == "__main__":
    terminal = Terminal()
    terminal.run()
