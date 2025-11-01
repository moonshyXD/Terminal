import argparse
import zipfile
from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch

from src.archive.unzip import Unzip
from src.utils.errors import NotAFileError, PathNotFoundError, ShellError


class TestsUnzip:
    """Тесты для Unzip"""

    def test_unzip_init(self) -> None:
        """
        Проверяет инициализацию Unzip
        """
        unzip = Unzip()

        assert isinstance(unzip, Unzip)

    def test_execute_extracts_zip_archive(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет распаковку zip архива
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        archive_path = make_temp_directory / "archive.zip"
        with zipfile.ZipFile(archive_path, "w") as zf:
            zf.writestr("file.txt", "content")

        monkeypatch.chdir(make_temp_directory)
        unzip = Unzip()

        tokens = argparse.Namespace(paths=[str(archive_path)])
        unzip.execute(tokens)

        extract_dir = make_temp_directory / "archive"
        assert extract_dir.exists()
        assert (extract_dir / "file.txt").exists()

    def test_execute_creates_directory_without_zip_extension(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет что директория создаётся без расширения .zip
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        archive_path = make_temp_directory / "myarchive.zip"
        with zipfile.ZipFile(archive_path, "w") as zf:
            zf.writestr("file.txt", "content")

        monkeypatch.chdir(make_temp_directory)
        unzip = Unzip()

        tokens = argparse.Namespace(paths=[str(archive_path)])
        unzip.execute(tokens)

        extract_dir = make_temp_directory / "myarchive"
        assert extract_dir.exists()
        assert not (make_temp_directory / "myarchive.zip.dir").exists()

    def test_execute_extracts_with_nested_files(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет распаковку архива с вложенными файлами
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        archive_path = make_temp_directory / "archive.zip"
        with zipfile.ZipFile(archive_path, "w") as zf:
            zf.writestr("file1.txt", "content1")
            zf.writestr("folder/file2.txt", "content2")
            zf.writestr("folder/subfolder/file3.txt", "content3")

        monkeypatch.chdir(make_temp_directory)
        unzip = Unzip()

        tokens = argparse.Namespace(paths=[str(archive_path)])
        unzip.execute(tokens)

        extract_dir = make_temp_directory / "archive"
        assert (extract_dir / "file1.txt").exists()
        assert (extract_dir / "folder" / "file2.txt").exists()
        assert (extract_dir / "folder" / "subfolder" / "file3.txt").exists()

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
        unzip = Unzip()

        tokens = argparse.Namespace(paths=[])

        with pytest.raises(ShellError):
            unzip.execute(tokens)

    def test_execute_nonexistent_archive_raises_error(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет ошибку при несуществующем архиве
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        :raises PathNotFoundError: При несуществующем архиве
        """
        nonexistent = make_temp_directory / "nonexistent.zip"

        monkeypatch.chdir(make_temp_directory)
        unzip = Unzip()

        tokens = argparse.Namespace(paths=[str(nonexistent)])

        with pytest.raises(PathNotFoundError):
            unzip.execute(tokens)

    def test_execute_directory_instead_of_file_raises_error(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет ошибку при попытке распаковать директорию
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        :raises NotAFileError: При попытке распаковать директорию
        """
        directory = make_temp_directory / "not_an_archive"
        directory.mkdir()

        monkeypatch.chdir(make_temp_directory)
        unzip = Unzip()

        tokens = argparse.Namespace(paths=[str(directory)])

        with pytest.raises(NotAFileError):
            unzip.execute(tokens)

    def test_unzip_method_extracts_correctly(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет что unzip распаковывает архив
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        archive_path = make_temp_directory / "archive.zip"
        with zipfile.ZipFile(archive_path, "w") as zf:
            zf.writestr("file.txt", "test content")

        extract_dir = make_temp_directory / "extract"

        monkeypatch.chdir(make_temp_directory)
        unzip = Unzip()

        unzip._unzip(str(archive_path), str(extract_dir))

        assert (extract_dir / "file.txt").exists()
        assert (extract_dir / "file.txt").read_text() == "test content"

    def test_execute_with_relative_path(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет распаковку с относительным путём
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        archive_path = make_temp_directory / "archive.zip"
        with zipfile.ZipFile(archive_path, "w") as zf:
            zf.writestr("file.txt", "content")

        monkeypatch.chdir(make_temp_directory)
        unzip = Unzip()

        tokens = argparse.Namespace(paths=["archive.zip"])
        unzip.execute(tokens)

        extract_dir = make_temp_directory / "archive"
        assert extract_dir.exists()

    def test_execute_empty_archive(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет распаковку пустого архива
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        archive_path = make_temp_directory / "empty.zip"
        with zipfile.ZipFile(archive_path, "w"):
            pass

        monkeypatch.chdir(make_temp_directory)
        unzip = Unzip()

        tokens = argparse.Namespace(paths=[str(archive_path)])
        unzip.execute(tokens)

        extract_dir = make_temp_directory / "empty"
        assert extract_dir.exists()

    def test_unzip_method_creates_extract_directory(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет что unzip создаёт директорию
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        archive_path = make_temp_directory / "archive.zip"
        with zipfile.ZipFile(archive_path, "w") as zf:
            zf.writestr("file.txt", "content")

        extract_dir = make_temp_directory / "new_extract_dir"

        monkeypatch.chdir(make_temp_directory)
        unzip = Unzip()

        assert not extract_dir.exists()

        unzip._unzip(str(archive_path), str(extract_dir))

        assert extract_dir.exists()

    def test_execute_preserves_file_contents(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет что содержимое файлов сохраняется
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        archive_path = make_temp_directory / "archive.zip"
        content = "Hello, World! 12345 !@#$%^&*()"

        with zipfile.ZipFile(archive_path, "w") as zf:
            zf.writestr("file.txt", content)

        monkeypatch.chdir(make_temp_directory)
        unzip = Unzip()

        tokens = argparse.Namespace(paths=[str(archive_path)])
        unzip.execute(tokens)

        extract_dir = make_temp_directory / "archive"
        extracted_content = (extract_dir / "file.txt").read_text()
        assert extracted_content == content

    def test_execute_multiple_nested_directories(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет распаковку с глубокой вложенностью директорий
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        archive_path = make_temp_directory / "archive.zip"
        with zipfile.ZipFile(archive_path, "w") as zip_file:
            zip_file.writestr("a/b/c/d/e/file.txt", "deep content")

        monkeypatch.chdir(make_temp_directory)
        unzip = Unzip()

        tokens = argparse.Namespace(paths=[str(archive_path)])
        unzip.execute(tokens)

        extract_dir = make_temp_directory / "archive"
        assert (
            extract_dir / "a" / "b" / "c" / "d" / "e" / "file.txt"
        ).exists()
