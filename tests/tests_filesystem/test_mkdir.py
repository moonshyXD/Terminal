import argparse
from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch

from src.filesystem.mkdir import Mkdir
from src.utils.errors import AlreadyExistsError, ShellError


class TestsMkdir:
    """Тесты для команды mkdir"""

    def test_mkdir_creates_directory(self, make_temp_directory: Path) -> None:
        """
        Проверяет создание директории
        :param make_temp_directory: Фикстура для временных директорий
        """
        new_dir = make_temp_directory / "newdir"

        tokens = argparse.Namespace(paths=[str(new_dir)])
        Mkdir().execute(tokens)

        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_mkdir_creates_multiple_directories(
        self, make_temp_directory: Path
    ) -> None:
        """
        Проверяет создание нескольких директорий
        :param make_temp_directory: Фикстура для временных директорий
        """
        dir1 = make_temp_directory / "dir1"
        dir2 = make_temp_directory / "dir2"
        dir3 = make_temp_directory / "dir3"

        tokens = argparse.Namespace(paths=[str(dir1), str(dir2), str(dir3)])
        Mkdir().execute(tokens)

        assert dir1.exists()
        assert dir2.exists()
        assert dir3.exists()

    def test_mkdir_empty_paths_raises_error(self) -> None:
        """
        Проверяет ошибку при пустом списке путей
        :raises ShellError: При пустом списке путей
        """
        tokens = argparse.Namespace(paths=[])
        with pytest.raises(ShellError):
            Mkdir().execute(tokens)

    def test_mkdir_already_exists_raises_error(
        self, make_temp_directory: Path
    ) -> None:
        """
        Проверяет ошибку при существующей директории
        :param make_temp_directory: Фикстура для временных директорий
        :raises AlreadyExistsError: При существующей директории
        """
        existing_dir = make_temp_directory / "existing"
        existing_dir.mkdir()

        tokens = argparse.Namespace(paths=[str(existing_dir)])
        with pytest.raises(AlreadyExistsError) as exc_info:
            Mkdir().execute(tokens)
        assert "уже создана" in str(exc_info.value)

    def test_mkdir_relative_path(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет создание директории по относительному пути
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения рабочей директории
        """
        monkeypatch.chdir(make_temp_directory)

        tokens = argparse.Namespace(paths=["newdir"])
        Mkdir().execute(tokens)

        new_dir = make_temp_directory / "newdir"
        assert new_dir.exists()

    def test_mkdir_absolute_path(self, make_temp_directory: Path) -> None:
        """
        Проверяет создание директории по абсолютному пути
        :param make_temp_directory: Фикстура для временных директорий
        """
        new_dir = make_temp_directory / "newdir"

        tokens = argparse.Namespace(paths=[str(new_dir.resolve())])
        Mkdir().execute(tokens)

        assert new_dir.exists()

    def test_mkdir_with_spaces_in_name(
        self, make_temp_directory: Path
    ) -> None:
        """
        Проверяет создание директории с пробелами в имени
        :param make_temp_directory: Фикстура для временных директорий
        """
        dir_with_spaces = make_temp_directory / "directory with spaces"

        tokens = argparse.Namespace(paths=[str(dir_with_spaces)])
        Mkdir().execute(tokens)

        assert dir_with_spaces.exists()

    def test_mkdir_nested_path_without_parent_raises_error(
        self, make_temp_directory: Path
    ) -> None:
        """
        Проверяет ошибку при создании вложенной директории без родительской
        :param make_temp_directory: Фикстура для временных директорий
        :raises FileNotFoundError: При отсутствии родительской директории
        """
        nested_dir = make_temp_directory / "parent" / "child"

        tokens = argparse.Namespace(paths=[str(nested_dir)])
        with pytest.raises(FileNotFoundError):
            Mkdir().execute(tokens)

    def test_mkdir_file_already_exists_raises_error(
        self, make_temp_directory: Path
    ) -> None:
        """
        Проверяет ошибку когда по пути уже существует файл
        :param make_temp_directory: Фикстура для временных директорий
        :raises AlreadyExistsError: При существующем файле
        """
        file = make_temp_directory / "file.txt"
        file.write_text("content")

        tokens = argparse.Namespace(paths=[str(file)])
        with pytest.raises(AlreadyExistsError):
            Mkdir().execute(tokens)

    def test_mkdir_creates_directory_in_subdirectory(
        self, make_temp_directory: Path
    ) -> None:
        """
        Проверяет создание директории внутри существующей
        :param make_temp_directory: Фикстура для временных директорий
        """
        parent = make_temp_directory / "parent"
        parent.mkdir()
        child = parent / "child"

        tokens = argparse.Namespace(paths=[str(child)])
        Mkdir().execute(tokens)

        assert child.exists()
