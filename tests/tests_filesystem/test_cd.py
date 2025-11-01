import argparse
import os
from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch

from src.filesystem.cd import Cd
from src.utils.errors import ShellError


class TestsCd:
    """Тесты для команды cd"""

    def test_cd_to_directory(self, make_temp_directory: Path) -> None:
        """
        Проверяет переход в директорию
        :param make_temp_directory: Фикстура для временных директорий
        """
        target_dir = make_temp_directory / "target"
        target_dir.mkdir()

        tokens = argparse.Namespace(paths=[str(target_dir)])
        Cd().execute(tokens)

        assert os.getcwd() == str(target_dir.resolve())

    def test_cd_without_path_goes_home(self) -> None:
        """
        Проверяет переход в домашнюю директорию при пустом paths
        """
        home_dir = Path.home()

        tokens = argparse.Namespace(paths=[])
        Cd().execute(tokens)

        assert os.getcwd() == str(home_dir)

    def test_cd_nonexistent_directory(self, make_temp_directory: Path) -> None:
        """
        Проверяет ошибку для несуществующей директории
        :param make_temp_directory: Фикстура для временных директорий
        :raises ShellError: При несуществующей директории
        """
        tokens = argparse.Namespace(
            paths=[str(make_temp_directory / "nonexistent")]
        )
        with pytest.raises(ShellError):
            Cd().execute(tokens)

    def test_cd_to_file_raises_error(self, make_temp_directory: Path) -> None:
        """
        Проверяет ошибку при попытке перейти в файл
        :param make_temp_directory: Фикстура для временных директорий
        :raises ShellError: При попытке перейти в файл
        """
        file = make_temp_directory / "file.txt"
        file.write_text("content")

        tokens = argparse.Namespace(paths=[str(file)])
        with pytest.raises(ShellError):
            Cd().execute(tokens)

    def test_cd_relative_path(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет переход по относительному пути
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения рабочей директории
        """
        subdirectory = make_temp_directory / "subdirectory"
        subdirectory.mkdir()
        monkeypatch.chdir(make_temp_directory)

        tokens = argparse.Namespace(paths=["subdirectory"])
        Cd().execute(tokens)

        assert os.getcwd() == str(subdirectory.resolve())

    def test_cd_to_parent_directory(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет переход в родительскую директорию с помощью ..
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения рабочей директории
        """
        subdirectory = make_temp_directory / "subdirectory"
        subdirectory.mkdir()
        monkeypatch.chdir(subdirectory)

        tokens = argparse.Namespace(paths=[".."])
        Cd().execute(tokens)

        assert os.getcwd() == str(make_temp_directory.resolve())

    def test_cd_absolute_path(self, make_temp_directory: Path) -> None:
        """
        Проверяет переход по абсолютному пути
        :param make_temp_directory: Фикстура для временных директорий
        """
        target_dir = make_temp_directory / "target"
        target_dir.mkdir()

        tokens = argparse.Namespace(paths=[str(target_dir.resolve())])
        Cd().execute(tokens)

        assert os.getcwd() == str(target_dir.resolve())

    def test_cd_with_tilde(self) -> None:
        """
        Проверяет переход с использованием ~
        """
        home_dir = Path.home()

        tokens = argparse.Namespace(paths=[])
        Cd().execute(tokens)

        assert os.getcwd() == str(home_dir)

    def test_cd_with_spaces_in_path(self, make_temp_directory: Path) -> None:
        """
        Проверяет переход в директорию с пробелами
        :param make_temp_directory: Фикстура для временных директорий
        """
        dir_with_spaces = make_temp_directory / "directory with spaces"
        dir_with_spaces.mkdir()

        tokens = argparse.Namespace(paths=[str(dir_with_spaces)])
        Cd().execute(tokens)

        assert os.getcwd() == str(dir_with_spaces.resolve())

    def test_cd_to_current_directory(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет переход в текущую директорию с помощью .
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения рабочей директории
        """
        monkeypatch.chdir(make_temp_directory)
        current = os.getcwd()

        tokens = argparse.Namespace(paths=["."])
        Cd().execute(tokens)

        assert os.getcwd() == current
