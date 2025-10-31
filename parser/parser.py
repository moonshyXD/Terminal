import argparse
from typing import Optional

from src.errors import ParserError


class Parser:
    """
    Класс для парсинга аргументов
    """

    def __init__(self) -> None:
        """
        Инициализация парсера
        """
        self.parser = argparse.ArgumentParser(
            description="Парсер для данных, введенных в терминал",
        )

        self.subparsers = self.parser.add_subparsers(
            dest="command",
            required=True,
            help="Команда для выполнения",
        )

        self._parser_setup()

    def parse(self, arguments: list) -> Optional[argparse.Namespace]:
        """
        Парсит список аргументов командной строки
        :param arguments: Список аргументов для парсинга
        :return: Распаршенные аргументы
        :raises ParserError: Если не удалось распарсить аргументы
        """
        try:
            parsed_arguments = self.parser.parse_args(arguments)

            return parsed_arguments
        except SystemExit as message:
            if message.code == 0:
                return None

            raise ParserError("Не удалось распарсить выражение") from None

    def _parser_setup(self) -> None:
        """
        Настраивает все доступные команды парсера
        """
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
        self._grep_setup()
        self._stop_setup()
        self._touch_setup()
        self._mkdir_setup()

    def _ls_setup(self) -> None:
        """
        Настраивает парсер для команды ls
        """
        ls_parser = self.subparsers.add_parser(
            "ls",
            help="Отображение списка файлов в текущем рабочем каталоге",
        )
        ls_parser.add_argument(
            "-l", action="store_true", help="Подробный вывод"
        )
        ls_parser.add_argument(
            "--all", "-a", action="store_true", help="Поддержка скрытых файлов"
        )
        ls_parser.add_argument(
            "-al",
            "-la",
            action="store_true",
            help="Подробный вывод файлов с поддержкой скрытых",
        )
        ls_parser.add_argument("paths", nargs="*", help="Пути к директориям")

    def _cd_setup(self) -> None:
        """
        Настраивает парсер для команды cd
        """
        cd_parser = self.subparsers.add_parser(
            "cd", help="Переход в указанный каталог"
        )
        cd_parser.add_argument("paths", nargs="*", help="Указанный каталог")

    def _cat_setup(self) -> None:
        """
        Настраивает парсер для команды cat
        """
        cat_parser = self.subparsers.add_parser(
            "cat", help="Вывод содержимого указанного файла в консоль"
        )
        cat_parser.add_argument("paths", nargs="*", help="Файлы для вывода")

    def _cp_setup(self) -> None:
        """
        Настраивает парсер для команды cp
        """
        cp_parser = self.subparsers.add_parser(
            "cp",
            help="Копирование файла или каталога из источника в назначение",
        )
        cp_parser.add_argument(
            "--recursive",
            "-r",
            action="store_true",
            help="Копирование директории",
        )
        cp_parser.add_argument(
            "paths", nargs="*", help="Исходный и целевой путь"
        )

    def _mv_setup(self) -> None:
        """
        Настраивает парсер для команды mv
        """
        mv_parser = self.subparsers.add_parser(
            "mv", help="Перемещение или переименование файла или каталога"
        )
        mv_parser.add_argument(
            "paths", nargs="*", help="Исходный и целевой путь"
        )

    def _rm_setup(self) -> None:
        """
        Настраивает парсер для команды rm
        """
        rm_parser = self.subparsers.add_parser(
            "rm", help="Удаление указанного файла"
        )
        rm_parser.add_argument(
            "--recursive",
            "-r",
            action="store_true",
            help="Рекурсивное удаление каталога",
        )
        rm_parser.add_argument(
            "paths", nargs="*", help="Файлы или директории для удаления"
        )

    def _history_setup(self) -> None:
        """
        Настраивает парсер для команды history
        """
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

    def _undo_setup(self) -> None:
        """
        Настраивает парсер для команды undo
        """
        self.subparsers.add_parser(
            "undo", help="Отменить последнюю команду из списка cp, mv, rm"
        )

    def _zip_setup(self) -> None:
        """
        Настраивает парсер для команды zip
        """
        zip_parser = self.subparsers.add_parser(
            "zip", help="Создание архива формата ZIP из каталога"
        )
        zip_parser.add_argument(
            "paths", nargs="*", help="Директория для архивации"
        )

    def _unzip_setup(self) -> None:
        """
        Настраивает парсер для команды unzip
        """
        unzip_parser = self.subparsers.add_parser(
            "unzip", help="Распаковка архива ZIP в текущий каталог"
        )
        unzip_parser.add_argument(
            "paths", nargs="*", help="Директория для разархивации"
        )

    def _tar_setup(self) -> None:
        """
        Настраивает парсер для команды tar
        """
        tar_parser = self.subparsers.add_parser(
            "tar", help="Создание архива формата TAR из каталога"
        )
        tar_parser.add_argument(
            "paths", nargs="*", help="Директория для архивации"
        )

    def _untar_setup(self) -> None:
        """
        Настраивает парсер для команды untar
        """
        untar_parser = self.subparsers.add_parser(
            "untar", help="Распаковка архива TAR в текущий каталог"
        )
        untar_parser.add_argument(
            "paths", nargs="*", help="Директория для разархивации"
        )

    def _grep_setup(self) -> None:
        """
        Настраивает парсер для команды grep
        """
        grep_parser = self.subparsers.add_parser(
            "grep", help="Поиск по указанному паттерну в файлах и подкаталогах"
        )
        grep_parser.add_argument(
            "--recursive",
            "-r",
            action="store_true",
            help="Рекурсивный поиск в подкаталогах",
        )
        grep_parser.add_argument(
            "--ignore-case",
            "-i",
            action="store_true",
            help="Поиск без учёта регистра",
        )
        grep_parser.add_argument("pattern", nargs=1, help="Шаблон для поиска")
        grep_parser.add_argument(
            "paths", nargs="*", help="Файлы или каталоги для поиска"
        )

    def _mkdir_setup(self) -> None:
        """
        Настраивает парсер для команды mkdir
        """
        mkdir_parser = self.subparsers.add_parser(
            "mkdir", help="Создание пустой директории"
        )
        mkdir_parser.add_argument(
            "paths", nargs="*", help="Директория для создания"
        )

    def _touch_setup(self) -> None:
        """
        Настраивает парсер для команды touch
        """
        touch_parser = self.subparsers.add_parser(
            "touch",
            help="Создание пустого файла/обновление времени модификации",
        )
        touch_parser.add_argument("paths", nargs="*", help="Файл для создания")

    def _stop_setup(self) -> None:
        """
        Настраивает парсер для команды stop
        """
        self.subparsers.add_parser("stop", help="Завершение работы программы")
