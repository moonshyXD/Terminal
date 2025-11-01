import argparse
from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch

from src.filesystem.touch import Touch
from src.utils.errors import ShellError


class TestsTouch:
    """Тесты для команды touch"""

    def test_touch_creates_file(self, make_temp_directory: Path) -> None:
        """
        Проверяет создание файла
        :param make_temp_directory: Фикстура для временных директорий
        """
        file = make_temp_directory / "newfile.txt"

        tokens = argparse.Namespace(paths=[str(file)])
        Touch().execute(tokens)

        assert file.exists()
        assert file.is_file()

    def test_touch_creates_multiple_files(
        self, make_temp_directory: Path
    ) -> None:
        """
        Проверяет создание нескольких файлов
        :param make_temp_directory: Фикстура для временных директорий
        """
        file1 = make_temp_directory / "file1.txt"
        file2 = make_temp_directory / "file2.txt"
        file3 = make_temp_directory / "file3.txt"

        tokens = argparse.Namespace(paths=[str(file1), str(file2), str(file3)])
        Touch().execute(tokens)

        assert file1.exists()
        assert file2.exists()
        assert file3.exists()

    def test_touch_empty_paths_raises_error(self) -> None:
        """
        Проверяет ошибку при пустом списке путей
        :raises ShellError: При пустом списке путей
        """
        tokens = argparse.Namespace(paths=[])
        with pytest.raises(ShellError):
            Touch().execute(tokens)

    def test_touch_relative_path(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет создание файла по относительному пути
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения рабочей директории
        """
        monkeypatch.chdir(make_temp_directory)

        tokens = argparse.Namespace(paths=["newfile.txt"])
        Touch().execute(tokens)

        file = make_temp_directory / "newfile.txt"
        assert file.exists()

    def test_touch_absolute_path(self, make_temp_directory: Path) -> None:
        """
        Проверяет создание файла по абсолютному пути
        :param make_temp_directory: Фикстура для временных директорий
        """
        file = make_temp_directory / "newfile.txt"

        tokens = argparse.Namespace(paths=[str(file.resolve())])
        Touch().execute(tokens)

        assert file.exists()

    def test_touch_updates_existing_file(
        self, make_temp_directory: Path
    ) -> None:
        """
        Проверяет обновление существующего файла
        :param make_temp_directory: Фикстура для временных директорий
        """
        file = make_temp_directory / "file.txt"
        file.write_text("old content")
        original_stat = file.stat()

        import time

        time.sleep(0.01)

        tokens = argparse.Namespace(paths=[str(file)])
        Touch().execute(tokens)

        new_stat = file.stat()
        assert new_stat.st_mtime > original_stat.st_mtime

    def test_touch_with_spaces_in_name(
        self, make_temp_directory: Path
    ) -> None:
        """
        Проверяет создание файла с пробелами в имени
        :param make_temp_directory: Фикстура для временных директорий
        """
        file = make_temp_directory / "file with spaces.txt"

        tokens = argparse.Namespace(paths=[str(file)])
        Touch().execute(tokens)

        assert file.exists()

    def test_touch_path_with_dots(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет создание файла с .. в пути
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения рабочей директории
        """
        subdir = make_temp_directory / "subdir"
        subdir.mkdir()
        monkeypatch.chdir(subdir)

        tokens = argparse.Namespace(paths=["../newfile.txt"])
        Touch().execute(tokens)

        file = make_temp_directory / "newfile.txt"
        assert file.exists()
