# src/main.py
import os
import shlex
import sys

from logger.logger import Logger
from parser.parser import Parser
from src.archive import tar, untar, unzip, zip
from src.errors import ShellError
from src.filesystem import cat, cd, cp, ls, mkdir, mv, rm, touch
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
        self.undo = undo.Undo()
        self.history = history.History()
        self.parser = Parser()

        self.COMMANDS = {
            "cat": cat.Cat().execute,
            "cd": cd.Cd().execute,
            "cp": cp.Cp().execute,
            "ls": ls.Ls().execute,
            "rm": rm.Rm().execute,
            "mv": mv.Mv().execute,
            "history": history.History().execute,
            "undo": undo.Undo().execute,
            "zip": zip.Zip().execute,
            "unzip": unzip.Unzip().execute,
            "tar": tar.Tar().execute,
            "untar": untar.Untar().execute,
            "grep": grep.Grep().execute,
            "mkdir": mkdir.Mkdir().execute,
            "touch": touch.Touch().execute,
        }

    def run(self) -> None:
        """
        Запуск терминала.
        Читает команды из stdin и выполняет их
        :raises ShellError: При ошибке выполнения команды
        """
        Logger.setup_logging()
        self.undo.clear_undo_history()

        print("Приветствуем вас в мини-оболочке с файловыми командами.")
        print("Для помощи в работе с командами пропишите в консоли --help")

        print(f"> {os.getcwd()} ", end="", flush=True)

        for line in sys.stdin:
            if not line.strip():
                print(f"> {os.getcwd()} ", end="", flush=True)
                continue

            Logger.start_execution(line.strip())
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

                Logger.success_execution(line.strip())
            except ShellError as message:
                print(message)
                Logger.failure_execution(str(message))

            print(f"> {os.getcwd()} ", end="", flush=True)


if __name__ == "__main__":
    terminal = Terminal()
    terminal.run()
