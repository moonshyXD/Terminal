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

        self._parser_setup()

    def parse(self, arguments: list):
        try:
            if not arguments:
                return None

            parsed_arguments = self.parser.parse_args(arguments)

            return parsed_arguments
        except SystemExit:
            raise ParserError("Не удалось распарсить выражение") from None

    def _parser_setup(self):
        self._cat_setup()
        self._cd_setup()
        self._cp_setup()
        self._history_setup()
        self._ls_setup()
        self._mv_setup()
        self._rm_setup()
        self._undo_setup()
        self._zip_setup()
        self._unzip_setup()
        self._tar_setup()
        self._untar_setup()

    def _ls_setup(self):
        ls_parser = self.subparsers.add_parser(
            "ls",
            help="Отображение списка файлов в текущем рабочем каталоге",
        )
        ls_parser.add_argument(
            "-l", action="store_true", help="Подробный вывод"
        )
        ls_parser.add_argument(
            "-long", action="store_true", help="Подробный вывод"
        )
        ls_parser.add_argument("paths", nargs="*", help="Пути к директориям")

    def _cd_setup(self):
        cd_parser = self.subparsers.add_parser(
            "cd", help="Переход в указанный каталог"
        )
        cd_parser.add_argument("paths", nargs="*", help="Указанный каталог")

    def _cat_setup(self):
        cat_parser = self.subparsers.add_parser(
            "cat", help="Вывод содержимиого указанного файла в консоль"
        )
        cat_parser.add_argument("paths", nargs="*", help="Файлы для вывода")

    def _cp_setup(self):
        cp_parser = self.subparsers.add_parser(
            "cp",
            help="Копирование файла или каталога из источника в назначение",
        )
        cp_parser.add_argument(
            "-r", action="store_true", help="Копирование директории"
        )
        cp_parser.add_argument(
            "-recursive", action="store_true", help="Копирование директории"
        )
        cp_parser.add_argument(
            "paths", nargs="*", help="Исходный и целевой путь"
        )

    def _mv_setup(self):
        mv_parser = self.subparsers.add_parser(
            "mv", help="Перемещение или переименовывание файла или каталога"
        )
        mv_parser.add_argument(
            "paths", nargs="*", help="Исходный и целевой путь"
        )

    def _rm_setup(self):
        rm_parser = self.subparsers.add_parser(
            "rm", help="Удаление указанного файла"
        )
        rm_parser.add_argument(
            "-r", action="store_true", help="Рекурсивное удаление каталога"
        )
        rm_parser.add_argument(
            "-recursive",
            action="store_true",
            help="Рекурсивное удаление каталога",
        )
        rm_parser.add_argument(
            "paths", nargs="*", help="Файлы или директории для удаления"
        )

    def _history_setup(self):
        history_parser = self.subparsers.add_parser(
            "history", help="Показать историю последних команд"
        )
        history_parser.add_argument(
            "count",
            type=int,
            nargs="?",
            default=10,
            help="Количество последних команд",
        )

    def _undo_setup(self):
        self.subparsers.add_parser(
            "undo", help="Отменить последнюю команду из списка cp, mv, rm"
        )

    def _zip_setup(self):
        zip_parser = self.subparsers.add_parser(
            "zip", help="Cоздание архива формата ZIP из каталога"
        )
        zip_parser.add_argument(
            "paths", nargs="*", help="Директория для архивации"
        )

    def _unzip_setup(self):
        unzip_parser = self.subparsers.add_parser(
            "unzip", help="Распаковка архива ZIP в текущий каталога"
        )
        unzip_parser.add_argument(
            "paths", nargs="*", help="Директория для разархивации"
        )

    def _tar_setup(self):
        tar_parser = self.subparsers.add_parser(
            "tar", help="Cоздание архива формата TAR из каталога"
        )
        tar_parser.add_argument(
            "paths", nargs="*", help="Директория для архивации"
        )

    def _untar_setup(self):
        untar_parser = self.subparsers.add_parser(
            "untar", help="Распаковка архива TAR в текущий каталога"
        )
        untar_parser.add_argument(
            "paths", nargs="*", help="Директория для разархивации"
        )
