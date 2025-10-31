import argparse
from pathlib import Path

import pytest
from _pytest.capture import CaptureFixture
from _pytest.monkeypatch import MonkeyPatch

from src.grep.grep import Grep
from src.utils.errors import (
    InvalidFileError,
    NotAFileError,
    RegualarVerbError,
    ShellError,
)


class TestsGrep:
    """Тесты для команды grep с 100% покрытием"""

    def test_grep_find_pattern_in_file(
        self, make_temp_directory: Path, capsys: CaptureFixture[str]
    ) -> None:
        """
        Проверяет поиск паттерна в файле
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        """
        file = make_temp_directory / "test.txt"
        file.write_text("hello world\nfoo bar\nhello again")

        tokens = argparse.Namespace(
            pattern=["hello"],
            paths=[str(file)],
            ignore_case=False,
            recursive=False,
            ri=False,
        )
        Grep().execute(tokens)
        captured = capsys.readouterr()

        assert "hello world" in captured.out
        assert "hello again" in captured.out

    def test_grep_ignore_case_flag(
        self, make_temp_directory: Path, capsys: CaptureFixture[str]
    ) -> None:
        """
        Проверяет флаг игнорирования регистра (покрывает tokens.ignore_case)
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        """
        file = make_temp_directory / "test.txt"
        file.write_text("Hello world\nFOO bar\nhello again")

        tokens = argparse.Namespace(
            pattern=["hello"],
            paths=[str(file)],
            ignore_case=True,
            recursive=False,
            ri=False,
        )
        Grep().execute(tokens)
        captured = capsys.readouterr()

        assert "Hello world" in captured.out
        assert "hello again" in captured.out

    def test_grep_ri_flag(
        self, make_temp_directory: Path, capsys: CaptureFixture[str]
    ) -> None:
        """
        Проверяет комбинированный флаг -ri (покрывает tokens.ri)
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        """
        (make_temp_directory / "file1.txt").write_text("Hello world")
        subdir = make_temp_directory / "subdir"
        subdir.mkdir()
        (subdir / "file2.txt").write_text("HELLO again")

        tokens = argparse.Namespace(
            pattern=["hello"],
            paths=[str(make_temp_directory)],
            ignore_case=False,
            recursive=False,
            ri=True,
        )
        Grep().execute(tokens)
        captured = capsys.readouterr()

        assert "Hello world" in captured.out
        assert "HELLO again" in captured.out

    def test_grep_no_matches(
        self, make_temp_directory: Path, capsys: CaptureFixture[str]
    ) -> None:
        """
        Проверяет случай когда нет совпадений
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        """
        file = make_temp_directory / "test.txt"
        file.write_text("foo bar\nbaz qux")

        tokens = argparse.Namespace(
            pattern=["hello"],
            paths=[str(file)],
            ignore_case=False,
            recursive=False,
            ri=False,
        )
        Grep().execute(tokens)
        captured = capsys.readouterr()

        assert "hello" not in captured.out

    def test_grep_line_numbers(
        self, make_temp_directory: Path, capsys: CaptureFixture[str]
    ) -> None:
        """
        Проверяет вывод номеров строк
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        """
        file = make_temp_directory / "test.txt"
        file.write_text("line1\nhello\nline3")

        tokens = argparse.Namespace(
            pattern=["hello"],
            paths=[str(file)],
            ignore_case=False,
            recursive=False,
            ri=False,
        )
        Grep().execute(tokens)
        captured = capsys.readouterr()

        assert ":2:" in captured.out

    def test_grep_unicode_decode_error(
        self, make_temp_directory: Path
    ) -> None:
        """
        Проверяет ошибку при невозможности прочитать файл
        :param make_temp_directory: Фикстура для временных директорий
        :raises InvalidFileError: При ошибке декодирования
        """
        file = make_temp_directory / "test.bin"
        file.write_bytes(b"\xff\xfe\xfd\x80\x81\x82")

        tokens = argparse.Namespace(
            pattern=["hello"],
            paths=[str(file)],
            ignore_case=False,
            recursive=False,
            ri=False,
        )
        with pytest.raises(InvalidFileError) as exc_info:
            Grep().execute(tokens)
        assert "невозможно прочитать" in str(exc_info.value)

    def test_grep_invalid_regex(self, make_temp_directory: Path) -> None:
        """
        Проверяет ошибку при неверном регулярном выражении
        :param make_temp_directory: Фикстура для временных директорий
        :raises RegualarVerbError: При неверном regex
        """
        file = make_temp_directory / "test.txt"
        file.write_text("hello world")

        tokens = argparse.Namespace(
            pattern=["[invalid(regex"],
            paths=[str(file)],
            ignore_case=False,
            recursive=False,
            ri=False,
        )
        with pytest.raises(RegualarVerbError):
            Grep().execute(tokens)

    def test_grep_default_path_uses_cwd(
        self,
        make_temp_directory: Path,
        capsys: CaptureFixture[str],
        monkeypatch: MonkeyPatch,
    ) -> None:
        """
        Проверяет использование текущей директории по умолчанию
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        :param monkeypatch: Фикстура для изменения окружения
        """
        file = make_temp_directory / "test.txt"
        file.write_text("hello world")
        monkeypatch.chdir(make_temp_directory)

        tokens = argparse.Namespace(
            pattern=["hello"],
            paths=[],
            ignore_case=False,
            recursive=True,
            ri=False,
        )
        Grep().execute(tokens)
        captured = capsys.readouterr()

        assert "hello world" in captured.out

    def test_grep_directory_without_recursive_raises_error(
        self, make_temp_directory: Path
    ) -> None:
        """
        Проверяет ошибку при директории без флага recursive
        :param make_temp_directory: Фикстура для временных директорий
        :raises NotAFileError: При попытке поиска в директории без -r
        """
        tokens = argparse.Namespace(
            pattern=["hello"],
            paths=[str(make_temp_directory)],
            ignore_case=False,
            recursive=False,
            ri=False,
        )
        with pytest.raises(NotAFileError):
            Grep().execute(tokens)

    def test_grep_recursive_search(
        self, make_temp_directory: Path, capsys: CaptureFixture[str]
    ) -> None:
        """
        Проверяет рекурсивный поиск
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        """
        (make_temp_directory / "file1.txt").write_text("hello world")
        subdir = make_temp_directory / "subdir"
        subdir.mkdir()
        (subdir / "file2.txt").write_text("hello again")

        tokens = argparse.Namespace(
            pattern=["hello"],
            paths=[str(make_temp_directory)],
            ignore_case=False,
            recursive=True,
            ri=False,
        )
        Grep().execute(tokens)
        captured = capsys.readouterr()

        assert "hello world" in captured.out
        assert "hello again" in captured.out

    def test_grep_nonexistent_file_raises_error(
        self, make_temp_directory: Path
    ) -> None:
        """
        Проверяет ошибку при несуществующем файле
        :param make_temp_directory: Фикстура для временных директорий
        :raises ShellError: При несуществующем файле
        """
        tokens = argparse.Namespace(
            pattern=["hello"],
            paths=[str(make_temp_directory / "nonexistent.txt")],
            ignore_case=False,
            recursive=False,
            ri=False,
        )
        with pytest.raises(ShellError):
            Grep().execute(tokens)

    def test_grep_multiple_files(
        self, make_temp_directory: Path, capsys: CaptureFixture[str]
    ) -> None:
        """
        Проверяет поиск в нескольких файлах
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        """
        file1 = make_temp_directory / "file1.txt"
        file2 = make_temp_directory / "file2.txt"
        file1.write_text("hello world")
        file2.write_text("hello again")

        tokens = argparse.Namespace(
            pattern=["hello"],
            paths=[str(file1), str(file2)],
            ignore_case=False,
            recursive=False,
            ri=False,
        )
        Grep().execute(tokens)
        captured = capsys.readouterr()

        assert "hello world" in captured.out
        assert "hello again" in captured.out

    def test_grep_empty_file(
        self, make_temp_directory: Path, capsys: CaptureFixture[str]
    ) -> None:
        """
        Проверяет поиск в пустом файле
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        """
        file = make_temp_directory / "empty.txt"
        file.write_text("")

        tokens = argparse.Namespace(
            pattern=["hello"],
            paths=[str(file)],
            ignore_case=False,
            recursive=False,
            ri=False,
        )
        Grep().execute(tokens)
        captured = capsys.readouterr()

        assert captured.out == ""
