import argparse
import os
import shutil
from collections import deque
from typing import List

from parser.parser import Parser
from src.errors import (
    CommandNotFoundError,
    PathNotFoundError,
    ShellError,
    UndoError,
)
from src.file_commands.base_command import BaseClass


class Undo(BaseClass):
    """
    Класс для отмены последних выполненных операций
    """

    def __init__(self) -> None:
        """
        Инициализация системы отмены
        """
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

    def execute(self, tokens: argparse.Namespace) -> None:
        """
        Отменяет последнюю выполненную операцию
        :param tokens: Аргументы команды
        :raises UndoError: Если нет команд для отмены
        :raises ShellError: При ошибке выполнения отмены
        """
        try:
            last_commands = self._get_last_command_group()

            if not last_commands:
                last_command = self._get_last_command()
                if not last_command:
                    raise UndoError("Команды для отмены не найдены")
                last_commands = [last_command]

            for cmd in last_commands:
                parsed_tokens = self.parser.parse(cmd.strip().split())

                if parsed_tokens is None:
                    continue

                if parsed_tokens.command in self.COMMANDS:
                    self.COMMANDS[parsed_tokens.command](parsed_tokens)

            self._remove_last_lines(len(last_commands))
        except Exception as message:
            raise ShellError(str(message)) from None

    def _get_last_command_group(self) -> List[str]:
        """
        Получает группу последних команд одного типа
        :return: Список последних команд одного типа
        :raises PathNotFoundError: Если файл истории не найден
        """
        try:
            with open(self.undo_history_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            if not lines:
                return []

            last_command = (
                lines[-1].strip().split()[0] if lines[-1].strip() else ""
            )

            if last_command in ["mv", "rm"]:
                result: List[str] = []
                for line in reversed(lines):
                    command = line.strip().split()[0] if line.strip() else ""
                    if command == last_command:
                        result.insert(0, line)
                    else:
                        break
                return result

            return []
        except FileNotFoundError:
            raise PathNotFoundError("Файл не найден") from None

    def _remove_last_lines(self, count: int) -> None:
        """
        Удаляет последние count строк из файла истории отмены
        :param count: Количество строк для удаления
        :raises PathNotFoundError: Если файл истории не найден
        """
        try:
            with open(self.undo_history_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            remaining = lines[:-count] if count < len(lines) else []

            with open(self.undo_history_path, "w", encoding="utf-8") as file:
                file.writelines(remaining)
        except FileNotFoundError:
            raise PathNotFoundError("Файл не найден") from None

    def _undo_cp(self, tokens: argparse.Namespace) -> None:
        """
        Отменяет операцию копирования
        Удаляет скопированный файл или директорию
        :param tokens: Аргументы команды (абсолютный путь к скопированному)
        """
        copied_path = tokens.paths[0]

        if os.path.exists(copied_path):
            if os.path.isdir(copied_path):
                shutil.rmtree(copied_path)
                print(f"Отменено копирование директории: {copied_path}")
            else:
                os.remove(copied_path)
                print(f"Отменено копирование файла: {copied_path}")
        else:
            print(f"Файл уже удалён: {copied_path}")

    def _undo_mv(self, tokens: argparse.Namespace) -> None:
        """
        Отменяет операцию перемещения
        :param tokens: Аргументы команды (пути к файлам)
        """
        abs_from_path = tokens.paths[0]
        abs_to_path = tokens.paths[1]

        shutil.move(abs_from_path, abs_to_path)

    def _undo_rm(self, tokens: argparse.Namespace) -> None:
        """
        Отменяет операцию удаления
        :param tokens: Аргументы команды (пути к файлам)
        """
        filename = tokens.paths[0]
        restore_dir = tokens.paths[1]

        abs_from_path = os.path.join(self.undo_trash_path, filename)
        abs_to_path = os.path.join(restore_dir, filename)

        shutil.move(abs_from_path, abs_to_path)

    def _get_last_command(self) -> str:
        """
        Получает последнюю команду из истории
        :return: Строка с последней командой
        :raises CommandNotFoundError: Если команда не найдена
        """
        try:
            with open(self.undo_history_path, "r", encoding="utf-8") as file:
                return "".join(deque(file, maxlen=1))
        except FileNotFoundError:
            raise CommandNotFoundError(
                "Команда для отмены не найдена"
            ) from None

    def add_undo_history(self, command: str) -> None:
        """
        Добавляет команду в историю отмены
        :param command: Команда для добавления
        """
        with open(self.undo_history_path, "a", encoding="utf-8") as file:
            file.write(f"{command}")

    def clear_undo_history(self) -> None:
        """
        Очищает историю отмены и корзину
        """
        with open(self.undo_history_path, "w") as _:
            pass
        shutil.rmtree(self.undo_trash_path)
        os.makedirs(self.undo_trash_path)
