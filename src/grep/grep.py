import argparse
import os
import re

from src.filesystem.base_command import BaseClass
from src.utils.errors import (
    InvalidFileError,
    NotAFileError,
    RegualarVerbError,
)


class Grep(BaseClass):
    """
    Класс для поиска текста по регулярному выражению в файлах
    """

    def execute(self, tokens: argparse.Namespace) -> None:
        """
        Выполняет поиск по паттерну в файлах и директориях
        :param tokens: Аргументы команды (паттерн, флаги, пути к файлам)
        :raises ShellError: При ошибке выполнения поиска
        """
        ignore_case = tokens.ignore_case or tokens.ri
        recursive = tokens.recursive or tokens.ri
        regex = self._is_correct_regular(tokens, ignore_case)
        paths = tokens.paths if tokens.paths else [os.getcwd()]

        self._grep_paths(paths, regex, recursive, ignore_case)

    def _grep_paths(
        self,
        paths: list,
        regex: re.Pattern,
        recursive: bool,
        ignore_case: bool,
    ) -> None:
        """
        Обрабатывает список путей для поиска
        :param paths: Список путей к файлам или директориям
        :param regex: Регулярное выражение
        :param recursive: Флаг рекурсивного поиска
        :param ignore_case: Флаг игнорирования регистра
        """
        for path in paths:
            abs_path = self._abs_path(path)
            self._path_exists(abs_path)

            if os.path.isfile(abs_path):
                self._find_coincidence(abs_path, regex, ignore_case)
            elif os.path.isdir(abs_path):
                if recursive:
                    for item in os.listdir(abs_path):
                        item_path = os.path.join(abs_path, item)
                        self._grep_paths(
                            [item_path], regex, recursive, ignore_case
                        )
                else:
                    raise NotAFileError(f"{abs_path} не является файлом")

    def _find_coincidence(
        self, file_path: str, regex: re.Pattern, ignore_case: bool
    ) -> None:
        """
        Ищет совпадения регулярного выражения в файле
        :param file_path: Путь к файлу для поиска
        :param regex: Регулярное выражение
        :param ignore_case: Флаг игнорирования регистра
        :raises InvalidFileError: Если файл невозможно прочитать
        """
        try:
            line_number = 1
            with open(file_path, "r", encoding="utf-8") as file:
                for line in file:
                    search_line = line.lower() if ignore_case else line

                    if regex.search(search_line):
                        print(f"{file_path}:{line_number}:{line.rstrip()}")

                    line_number += 1
        except UnicodeDecodeError:
            raise InvalidFileError(
                f"Файл {file_path} невозможно прочитать"
            ) from None

    def _is_correct_regular(
        self, tokens: argparse.Namespace, ignore_case: bool
    ):
        """
        Компилирует регулярное выражение с учётом флагов
        :param tokens: Аргументы команды (паттерн)
        :return: Скомпилированное регулярное выражение
        :raises RegualarVerbError: Неверное регулярное выражение
        """
        try:
            regex = "".join(tokens.pattern[0])
            compiled_regex = (
                re.compile(regex, re.IGNORECASE)
                if ignore_case
                else re.compile(regex)
            )
            return compiled_regex
        except re.error:
            raise RegualarVerbError(
                "Неккоректное регулярное выражение"
            ) from None
