import pytest

from src.utils.errors import ParserError
from src.utils.parser import NoErrorParser, Parser


class TestsNoErrorParser:
    """Тесты для NoErrorParser"""

    def test_no_error_parser_raises_parser_error(self) -> None:
        """
        Проверяет что NoErrorParser выбрасывает ParserError вместо вывода
        :raises ParserError: При ошибке парсинга
        """
        parser = NoErrorParser()

        with pytest.raises(ParserError) as exc_info:
            parser.error("Test error message")

        assert "Не удалось распарсить выражение" in str(exc_info.value)


class TestsParser:
    """Тесты для Parser"""

    def test_parser_init(self) -> None:
        """
        Проверяет инициализацию парсера
        """
        parser = Parser()

        assert parser.parser is not None
        assert parser.subparsers is not None
        assert isinstance(parser.parser, NoErrorParser)

    def test_parse_ls_command(self) -> None:
        """
        Проверяет парсинг команды ls
        """
        parser = Parser()
        result = parser.parse(["ls", "/home"])

        assert result is not None
        assert result.command == "ls"
        assert result.paths == ["/home"]

    def test_parse_ls_with_flags(self) -> None:
        """
        Проверяет парсинг ls с флагами
        """
        parser = Parser()
        result = parser.parse(["ls", "-l", "-a", "/home"])

        assert result is not None
        assert result.command == "ls"
        assert result.l is True
        assert result.all is True
        assert result.paths == ["/home"]

    def test_parse_ls_with_al_flag(self) -> None:
        """
        Проверяет парсинг ls с флагом -al
        """
        parser = Parser()
        result = parser.parse(["ls", "-al", "/home"])

        assert result is not None
        assert result.command == "ls"
        assert result.al is True

    def test_parse_cd_command(self) -> None:
        """
        Проверяет парсинг команды cd
        """
        parser = Parser()
        result = parser.parse(["cd", "/home"])

        assert result is not None
        assert result.command == "cd"
        assert result.paths == ["/home"]

    def test_parse_cat_command(self) -> None:
        """
        Проверяет парсинг команды cat
        """
        parser = Parser()
        result = parser.parse(["cat", "file.txt"])

        assert result is not None
        assert result.command == "cat"
        assert result.paths == ["file.txt"]

    def test_parse_cp_command(self) -> None:
        """
        Проверяет парсинг команды cp
        """
        parser = Parser()
        result = parser.parse(["cp", "source.txt", "dest.txt"])

        assert result is not None
        assert result.command == "cp"
        assert result.recursive is False
        assert result.paths == ["source.txt", "dest.txt"]

    def test_parse_cp_with_recursive_flag(self) -> None:
        """
        Проверяет парсинг cp с флагом -r
        """
        parser = Parser()
        result = parser.parse(["cp", "-r", "source_dir", "dest_dir"])

        assert result is not None
        assert result.command == "cp"
        assert result.recursive is True

    def test_parse_mv_command(self) -> None:
        """
        Проверяет парсинг команды mv
        """
        parser = Parser()
        result = parser.parse(["mv", "old_name.txt", "new_name.txt"])

        assert result is not None
        assert result.command == "mv"
        assert result.paths == ["old_name.txt", "new_name.txt"]

    def test_parse_rm_command(self) -> None:
        """
        Проверяет парсинг команды rm
        """
        parser = Parser()
        result = parser.parse(["rm", "file.txt"])

        assert result is not None
        assert result.command == "rm"
        assert result.recursive is False

    def test_parse_rm_with_recursive_flag(self) -> None:
        """
        Проверяет парсинг rm с флагом -r
        """
        parser = Parser()
        result = parser.parse(["rm", "-r", "directory"])

        assert result is not None
        assert result.command == "rm"
        assert result.recursive is True

    def test_parse_history_command(self) -> None:
        """
        Проверяет парсинг команды history
        """
        parser = Parser()
        result = parser.parse(["history", "20"])

        assert result is not None
        assert result.command == "history"
        assert result.count == 20

    def test_parse_history_default_count(self) -> None:
        """
        Проверяет значение count по умолчанию
        """
        parser = Parser()
        result = parser.parse(["history"])

        assert result is not None
        assert result.command == "history"
        assert result.count == 10

    def test_parse_undo_command(self) -> None:
        """
        Проверяет парсинг команды undo
        """
        parser = Parser()
        result = parser.parse(["undo"])

        assert result is not None
        assert result.command == "undo"

    def test_parse_zip_command(self) -> None:
        """
        Проверяет парсинг команды zip
        """
        parser = Parser()
        result = parser.parse(["zip", "directory"])

        assert result is not None
        assert result.command == "zip"
        assert result.paths == ["directory"]

    def test_parse_unzip_command(self) -> None:
        """
        Проверяет парсинг команды unzip
        """
        parser = Parser()
        result = parser.parse(["unzip", "archive.zip"])

        assert result is not None
        assert result.command == "unzip"
        assert result.paths == ["archive.zip"]

    def test_parse_tar_command(self) -> None:
        """
        Проверяет парсинг команды tar
        """
        parser = Parser()
        result = parser.parse(["tar", "directory"])

        assert result is not None
        assert result.command == "tar"
        assert result.paths == ["directory"]

    def test_parse_untar_command(self) -> None:
        """
        Проверяет парсинг команды untar
        """
        parser = Parser()
        result = parser.parse(["untar", "archive.tar"])

        assert result is not None
        assert result.command == "untar"
        assert result.paths == ["archive.tar"]

    def test_parse_grep_command(self) -> None:
        """
        Проверяет парсинг команды grep
        """
        parser = Parser()
        result = parser.parse(["grep", "pattern", "file.txt"])

        assert result is not None
        assert result.command == "grep"
        assert result.pattern == ["pattern"]
        assert result.paths == ["file.txt"]

    def test_parse_grep_with_recursive_flag(self) -> None:
        """
        Проверяет парсинг grep с флагом -r
        """
        parser = Parser()
        result = parser.parse(["grep", "-r", "pattern", "directory"])

        assert result is not None
        assert result.command == "grep"
        assert result.recursive is True

    def test_parse_grep_with_ignore_case_flag(self) -> None:
        """
        Проверяет парсинг grep с флагом -i
        """
        parser = Parser()
        result = parser.parse(["grep", "-i", "pattern", "file.txt"])

        assert result is not None
        assert result.command == "grep"
        assert result.ignore_case is True

    def test_parse_grep_with_ri_flag(self) -> None:
        """
        Проверяет парсинг grep с флагом -ri
        """
        parser = Parser()
        result = parser.parse(["grep", "-ri", "pattern", "directory"])

        assert result is not None
        assert result.command == "grep"
        assert result.ri is True

    def test_parse_mkdir_command(self) -> None:
        """
        Проверяет парсинг команды mkdir
        """
        parser = Parser()
        result = parser.parse(["mkdir", "new_dir"])

        assert result is not None
        assert result.command == "mkdir"
        assert result.paths == ["new_dir"]

    def test_parse_touch_command(self) -> None:
        """
        Проверяет парсинг команды touch
        """
        parser = Parser()
        result = parser.parse(["touch", "file.txt"])

        assert result is not None
        assert result.command == "touch"
        assert result.paths == ["file.txt"]

    def test_parse_stop_command(self) -> None:
        """
        Проверяет парсинг команды stop
        """
        parser = Parser()
        result = parser.parse(["stop"])

        assert result is not None
        assert result.command == "stop"

    def test_parse_invalid_command_raises_error(self) -> None:
        """
        Проверяет ошибку при неверной команде
        :raises ParserError: При неверной команде
        """
        parser = Parser()

        with pytest.raises(ParserError):
            parser.parse(["invalid_command"])

    def test_parse_no_command_raises_error(self) -> None:
        """
        Проверяет ошибку при отсутствии команды
        :raises ParserError: При отсутствии команды
        """
        parser = Parser()

        with pytest.raises(ParserError):
            parser.parse([])

    def test_parse_system_exit_with_zero_code(self) -> None:
        """
        Проверяет обработку SystemExit с кодом 0
        """
        parser = Parser()
        result = parser.parse(["--help"])

        assert result is None

    def test_parse_multiple_paths(self) -> None:
        """
        Проверяет парсинг нескольких путей
        """
        parser = Parser()
        result = parser.parse(["cat", "file1.txt", "file2.txt", "file3.txt"])

        assert result is not None
        assert result.command == "cat"
        assert result.paths == ["file1.txt", "file2.txt", "file3.txt"]

    def test_parse_ls_empty_paths(self) -> None:
        """
        Проверяет парсинг ls без путей
        """
        parser = Parser()
        result = parser.parse(["ls"])

        assert result is not None
        assert result.command == "ls"
        assert result.paths == []

    def test_parse_grep_multiple_paths(self) -> None:
        """
        Проверяет парсинг grep с несколькими путями
        """
        parser = Parser()
        result = parser.parse(["grep", "pattern", "file1.txt", "file2.txt"])

        assert result is not None
        assert result.command == "grep"
        assert result.pattern == ["pattern"]
        assert result.paths == ["file1.txt", "file2.txt"]

    def test_parser_setup_called_during_init(self) -> None:
        """
        Проверяет что все setup методы вызываются
        """
        parser = Parser()

        commands = [
            "ls",
            "cd",
            "cat",
            "cp",
            "mv",
            "rm",
            "history",
            "undo",
            "zip",
            "unzip",
            "tar",
            "untar",
            "grep",
            "mkdir",
            "touch",
            "stop",
        ]

        for command in commands:
            result = parser.parse(
                [command]
                if command in ["undo", "stop", "history"]
                else [command, "arg"]
            )
            assert result is not None
            assert result.command == command
