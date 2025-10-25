import argparse

from src.errors import ParserError


class Parser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Парсер для данных, введенных в терминал",
        )

        self.subparsers = self.parser.add_subparsers(
            dest="command",
            required=True,
            help="Команда для выполнения",
        )

        self._setup()

    def _setup(self):
        ls_parser = self.subparsers.add_parser(
            "ls",
            help="Отображение списка файлов в текущем рабочем каталоге",
        )
        ls_parser.add_argument(
            "-l", action="store_true", help="Подробный вывод"
        )
        ls_parser.add_argument("paths", nargs="*", help="Пути к директориям")

        cat_parser = self.subparsers.add_parser(
            "cat", help="Вывод содержимиого указанного файла в консоль"
        )
        cat_parser.add_argument("paths", nargs="*", help="Файлы для вывода")

        cp_parser = self.subparsers.add_parser(
            "cp",
            help="Копирование файла или каталога из источника в назначение",
        )
        cp_parser.add_argument(
            "-r", action="store_true", help="Копирование директории"
        )
        cp_parser.add_argument(
            "paths", nargs="*", help="Исходный и целевой путь"
        )

        mv_parser = self.subparsers.add_parser(
            "mv", help="Перемещение или переименовывание файла или каталога"
        )
        mv_parser.add_argument(
            "paths", nargs="*", help="Исходный и целевой путь"
        )

        rm_parser = self.subparsers.add_parser(
            "rm", help="Удаление указанного файла"
        )
        rm_parser.add_argument(
            "-r", action="store_true", help="Рекурсивное удаление каталога"
        )
        rm_parser.add_argument(
            "paths", nargs="*", help="Файлы или директории для удаления"
        )

        cd_parser = self.subparsers.add_parser(
            "cd", help="Переход в указанный каталог"
        )
        cd_parser.add_argument("paths", nargs=1, help="Указанный каталог")

    def parse(self, arguments: list):
        try:
            if not arguments:
                return None

            parsed_arguments = self.parser.parse_args(arguments)

            return parsed_arguments
        except SystemExit:
            raise ParserError("Не удалось распарсить выражение") from None
