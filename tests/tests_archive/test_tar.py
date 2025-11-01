import argparse
import tarfile
from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch

from src.archive.tar import Tar
from src.utils.errors import NotADirectoryError, PathNotFoundError, ShellError


class TestsTar:
    """Тесты для Tar"""

    def test_tar_init(self) -> None:
        """
        Проверяет инициализацию Tar
        """
        tar = Tar()

        assert isinstance(tar, Tar)

    def test_execute_creates_tar_gz_with_default_name(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет создание архива с именем по умолчанию
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        folder = make_temp_directory / "folder_to_tar"
        folder.mkdir()
        (folder / "file.txt").write_text("goose")

        monkeypatch.chdir(make_temp_directory)
        tar = Tar()

        tokens = argparse.Namespace(paths=[str(folder)])
        tar.execute(tokens)

        archive_path = make_temp_directory / "folder_to_tar.tar.gz"
        assert archive_path.exists()

    def test_execute_creates_tar_gz_with_custom_name(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет создание архива с указанным именем
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        folder = make_temp_directory / "folder_to_tar"
        folder.mkdir()
        (folder / "file.txt").write_text("goose")

        custom_archive = make_temp_directory / "custom_name.tar.gz"

        monkeypatch.chdir(make_temp_directory)
        tar = Tar()

        tokens = argparse.Namespace(paths=[str(folder), str(custom_archive)])
        tar.execute(tokens)

        assert custom_archive.exists()

    def test_execute_adds_tar_gz_extension_if_missing(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет добавление расширения .tar.gz
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        folder = make_temp_directory / "folder_to_tar"
        folder.mkdir()
        (folder / "file.txt").write_text("goose")

        archive_without_ext = make_temp_directory / "archive"

        monkeypatch.chdir(make_temp_directory)
        tar = Tar()

        tokens = argparse.Namespace(
            paths=[str(folder), str(archive_without_ext)]
        )
        tar.execute(tokens)

        assert (make_temp_directory / "archive.tar.gz").exists()

    def test_execute_preserves_tgz_extension(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет что .tgz расширение не переписывается
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        folder = make_temp_directory / "folder_to_tar"
        folder.mkdir()
        (folder / "file.txt").write_text("goose")

        archive_tgz = make_temp_directory / "archive.tgz"

        monkeypatch.chdir(make_temp_directory)
        tar = Tar()

        tokens = argparse.Namespace(paths=[str(folder), str(archive_tgz)])
        tar.execute(tokens)

        assert archive_tgz.exists()

    def test_execute_with_nested_files(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет архивацию папки с вложенными файлами
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        folder = make_temp_directory / "folder_to_tar"
        folder.mkdir()
        subdir = folder / "subdir"
        subdir.mkdir()
        (folder / "file1.txt").write_text("goose1")
        (subdir / "file2.txt").write_text("goose2")

        monkeypatch.chdir(make_temp_directory)
        tar = Tar()

        tokens = argparse.Namespace(paths=[str(folder)])
        tar.execute(tokens)

        archive_path = make_temp_directory / "folder_to_tar.tar.gz"
        assert archive_path.exists()

        with tarfile.open(archive_path, "r:gz") as tar_file:
            members = tar_file.getnames()
            assert any("file1.txt" in m for m in members)
            assert any("file2.txt" in m for m in members)

    def test_execute_empty_directory(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет архивацию пустой директории
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        folder = make_temp_directory / "empty_folder"
        folder.mkdir()

        monkeypatch.chdir(make_temp_directory)
        tar = Tar()

        tokens = argparse.Namespace(paths=[str(folder)])
        tar.execute(tokens)

        archive_path = make_temp_directory / "empty_folder.tar.gz"
        assert archive_path.exists()

    def test_execute_no_paths_raises_error(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет ошибку при отсутствии путей
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        :raises ShellError: При отсутствии путей
        """
        monkeypatch.chdir(make_temp_directory)
        tar = Tar()

        tokens = argparse.Namespace(paths=[])

        with pytest.raises(ShellError):
            tar.execute(tokens)

    def test_execute_nonexistent_directory_raises_error(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет ошибку при несуществующей директории
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        :raises PathNotFoundError: При несуществующей директории
        """
        nonexistent = make_temp_directory / "nonexistent"

        monkeypatch.chdir(make_temp_directory)
        tar = Tar()

        tokens = argparse.Namespace(paths=[str(nonexistent)])

        with pytest.raises(PathNotFoundError):
            tar.execute(tokens)

    def test_execute_file_instead_of_directory_raises_error(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет ошибку при попытке архивировать файл
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        :raises NotADirectoryError: При попытке архивировать файл
        """
        file = make_temp_directory / "file.txt"
        file.write_text("goose")

        monkeypatch.chdir(make_temp_directory)
        tar = Tar()

        tokens = argparse.Namespace(paths=[str(file)])

        with pytest.raises(NotADirectoryError):
            tar.execute(tokens)

    def test_execute_with_relative_path(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет архивацию с относительным путём
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        folder = make_temp_directory / "folder_to_tar"
        folder.mkdir()
        (folder / "file.txt").write_text("goose")

        monkeypatch.chdir(make_temp_directory)
        tar = Tar()

        tokens = argparse.Namespace(paths=["folder_to_tar"])
        tar.execute(tokens)

        archive_path = make_temp_directory / "folder_to_tar.tar.gz"
        assert archive_path.exists()
