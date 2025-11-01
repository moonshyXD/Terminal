import argparse
from pathlib import Path

import pytest
from _pytest.capture import CaptureFixture
from _pytest.monkeypatch import MonkeyPatch

from src.filesystem.cat import Cat
from src.utils.errors import ShellError


class TestsCat:
    """Тесты для команды cat"""

    def test_cat_displays_file_content(
        self, make_temp_file: Path, capsys: CaptureFixture[str]
    ) -> None:
        """
        Проверяет что cat выводит содержимое файла в консоль
        :param make_temp_file: Фикстура с тестовым файлом
        :param capsys: Фикстура для захвата stdout
        """
        tokens = argparse.Namespace(paths=[str(make_temp_file)])
        Cat().execute(tokens)
        content = capsys.readouterr()
        assert "Temp" in content.out

    def test_cat_multiple_files(
        self, make_temp_directory: Path, capsys: CaptureFixture[str]
    ) -> None:
        """
        Проверяет что cat выводит содержимое нескольких файлов
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        """
        file1 = make_temp_directory / "file1.txt"
        file2 = make_temp_directory / "file2.txt"
        file1.write_text("Temp1")
        file2.write_text("Temp2")

        tokens = argparse.Namespace(paths=[str(file1), str(file2)])
        Cat().execute(tokens)
        captured = capsys.readouterr()
        assert "Temp1" in captured.out
        assert "Temp2" in captured.out

    def test_cat_empty_file(
        self, make_temp_directory: Path, capsys: CaptureFixture[str]
    ) -> None:
        """
        Проверяет что cat корректно работает с пустым файлом
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        """
        empty = make_temp_directory / "empty.txt"
        empty.write_text("")
        tokens = argparse.Namespace(paths=[str(empty)])
        Cat().execute(tokens)
        captured = capsys.readouterr()
        assert "\n" in captured.out

    def test_cat_no_paths_raises_error(self) -> None:
        """
        Проверяет что cat выдаёт ошибку при отсутствии аргументов
        :raises ShellError: При вызове без путей к файлам
        """
        tokens = argparse.Namespace(paths=[])
        with pytest.raises(ShellError):
            Cat().execute(tokens)

    def test_cat_nonexistent_file(self, make_temp_directory: Path) -> None:
        """
        Проверяет что cat выдаёт ошибку для несуществующего файла
        :param make_temp_directory: Фикстура для временных директорий
        :raises ShellError: При попытке прочитать несуществующий файл
        """
        tokens = argparse.Namespace(
            paths=[str(make_temp_directory / "nonexistent.txt")]
        )
        with pytest.raises(ShellError):
            Cat().execute(tokens)

    def test_cat_directory_raises_error(
        self, make_temp_directory: Path
    ) -> None:
        """
        Проверяет что cat выдаёт ошибку при попытке прочитать директорию
        :param make_temp_directory: Фикстура для временных директорий
        :raises ShellError: При попытке прочитать директорию
        """
        directory = make_temp_directory / "testdirectory"
        directory.mkdir()
        tokens = argparse.Namespace(paths=[str(directory)])
        with pytest.raises(ShellError):
            Cat().execute(tokens)

    def test_cat_permission_denied(self, make_temp_directory: Path) -> None:
        """
        Проверяет что cat выдаёт ошибку для файла без прав чтения
        :param make_temp_directory: Фикстура для временных директорий
        :raises ShellError: При отсутствии прав на чтение
        """
        no_read_file = make_temp_directory / "no_read.txt"
        no_read_file.write_text("secret")
        no_read_file.chmod(0o000)

        try:
            tokens = argparse.Namespace(paths=[str(no_read_file)])
            with pytest.raises(ShellError):
                Cat().execute(tokens)
        finally:
            no_read_file.chmod(0o644)

    def test_cat_absolute_path(
        self, make_temp_file: Path, capsys: CaptureFixture[str]
    ) -> None:
        """
        Проверяет работу cat с абсолютным путём
        :param make_temp_file: Фикстура с тестовым файлом
        :param capsys: Фикстура для захвата stdout
        """
        absolute_path = make_temp_file.resolve()
        tokens = argparse.Namespace(paths=[str(absolute_path)])
        Cat().execute(tokens)
        content = capsys.readouterr()
        assert "Temp" in content.out

    def test_cat_relative_path(
        self,
        make_temp_directory: Path,
        capsys: CaptureFixture[str],
        monkeypatch: MonkeyPatch,
    ) -> None:
        """
        Проверяет работу cat с относительным путём
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        :param monkeypatch: Фикстура для изменения рабочей директории
        """
        file = make_temp_directory / "relative.txt"
        file.write_text("relative")

        monkeypatch.chdir(make_temp_directory)

        tokens = argparse.Namespace(paths=["relative.txt"])
        Cat().execute(tokens)
        content = capsys.readouterr()
        assert "relative" in content.out

    def test_cat_path_with_dots(
        self,
        make_temp_directory: Path,
        capsys: CaptureFixture[str],
        monkeypatch: MonkeyPatch,
    ) -> None:
        """
        Проверяет работу cat с путём содержащим .. и .
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        :param monkeypatch: Фикстура для изменения рабочей директории
        """
        subdirectory = make_temp_directory / "subdirectory"
        subdirectory.mkdir()
        file = make_temp_directory / "file.txt"
        file.write_text("Temp")

        monkeypatch.chdir(subdirectory)

        tokens = argparse.Namespace(paths=["../file.txt"])
        Cat().execute(tokens)
        content = capsys.readouterr()
        assert "Temp" in content.out

    def test_cat_path_with_spaces(
        self, make_temp_directory: Path, capsys: CaptureFixture[str]
    ) -> None:
        """
        Проверяет работу cat с путём содержащим пробелы
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        """
        file_with_spaces = make_temp_directory / "file with spaces.txt"
        file_with_spaces.write_text("with spaces")

        tokens = argparse.Namespace(paths=[str(file_with_spaces)])
        Cat().execute(tokens)
        content = capsys.readouterr()
        assert "with spaces" in content.out

    def test_cat_large_file(
        self, make_temp_directory: Path, capsys: CaptureFixture[str]
    ) -> None:
        """
        Проверяет работу cat с большим файлом
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        """
        large_file = make_temp_directory / "large.txt"
        content = "line\n" * 1000
        large_file.write_text(content)

        tokens = argparse.Namespace(paths=[str(large_file)])
        Cat().execute(tokens)
        captured = capsys.readouterr()
        assert captured.out.count("line") == 1000

    def test_cat_file_with_special_chars(
        self, make_temp_directory: Path, capsys: CaptureFixture[str]
    ) -> None:
        """
        Проверяет работу cat с файлом содержащим спецсимволы
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        """
        special = make_temp_directory / "special.txt"
        special.write_text("!@#$%^&*()_+-={}[]|\\:;\"'<>,.?/~`")

        tokens = argparse.Namespace(paths=[str(special)])
        Cat().execute(tokens)
        content = capsys.readouterr()
        assert "!@#$%^&*()" in content.out

    def test_cat_unicode_content(
        self, make_temp_directory: Path, capsys: CaptureFixture[str]
    ) -> None:
        """
        Проверяет работу cat с Unicode содержимым
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        """
        unicode_file = make_temp_directory / "unicode.txt"
        unicode_file.write_text("Привет 世界", encoding="utf-8")

        tokens = argparse.Namespace(paths=[str(unicode_file)])
        Cat().execute(tokens)
        content = capsys.readouterr()
        assert "Привет" in content.out
        assert "世界" in content.out

    def test_cat_file_with_tabs_and_newlines(
        self, make_temp_directory: Path, capsys: CaptureFixture[str]
    ) -> None:
        """
        Проверяет работу cat с табуляцией и переводами строк
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        """
        formatted = make_temp_directory / "formatted.txt"
        formatted.write_text("line1\tcolumn2\nline2\tcolumn2")

        tokens = argparse.Namespace(paths=[str(formatted)])
        Cat().execute(tokens)
        content = capsys.readouterr()
        assert "\t" in content.out
        assert "line1" in content.out
        assert "line2" in content.out

    def test_cat_hidden_file(
        self, make_temp_directory: Path, capsys: CaptureFixture[str]
    ) -> None:
        """
        Проверяет работу cat со скрытым файлом
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        """
        hidden = make_temp_directory / ".hidden"
        hidden.write_text("Hidden content")

        tokens = argparse.Namespace(paths=[str(hidden)])
        Cat().execute(tokens)
        content = capsys.readouterr()
        assert "Hidden content" in content.out

    def test_cat_mixed_paths_absolute_and_relative(
        self,
        make_temp_directory: Path,
        capsys: CaptureFixture[str],
        monkeypatch: MonkeyPatch,
    ) -> None:
        """
        Проверяет работу cat со смешанными путями
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        :param monkeypatch: Фикстура для изменения рабочей директории
        """
        absolute = make_temp_directory / "absolute.txt"
        relative = make_temp_directory / "relative.txt"
        absolute.write_text("absolute")
        relative.write_text("relative")

        monkeypatch.chdir(make_temp_directory)

        tokens = argparse.Namespace(
            paths=[str(absolute.resolve()), "relative.txt"]
        )
        Cat().execute(tokens)
        content = capsys.readouterr()
        assert "absolute" in content.out
        assert "relative" in content.out

    def test_cat_files_output_order(
        self, make_temp_directory: Path, capsys: CaptureFixture[str]
    ) -> None:
        """
        Проверяет что cat выводит файлы в правильном порядке
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        """
        file1 = make_temp_directory / "file1.txt"
        file2 = make_temp_directory / "file2.txt"
        file3 = make_temp_directory / "file3.txt"
        file1.write_text("file1")
        file2.write_text("file2")
        file3.write_text("file3")

        tokens = argparse.Namespace(paths=[str(file1), str(file2), str(file3)])
        Cat().execute(tokens)
        content = capsys.readouterr()

        first_pos = content.out.find("file1")
        second_pos = content.out.find("file2")
        third_pos = content.out.find("file3")

        assert first_pos < second_pos < third_pos
