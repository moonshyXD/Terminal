import argparse
import zipfile
from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch

from src.archive.zip import Zip
from src.utils.errors import NotADirectoryError, PathNotFoundError, ShellError


class TestsZip:
    """Тесты для Zip с 100% покрытием"""

    def test_zip_init(self) -> None:
        """
        Проверяет инициализацию Zip
        """
        zip_obj = Zip()

        assert isinstance(zip_obj, Zip)

    def test_execute_creates_zip_with_default_name(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет создание архива с именем по умолчанию
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        folder = make_temp_directory / "folder_to_zip"
        folder.mkdir()
        (folder / "file.txt").write_text("content")

        monkeypatch.chdir(make_temp_directory)
        zip_obj = Zip()

        tokens = argparse.Namespace(paths=[str(folder)])
        zip_obj.execute(tokens)

        archive_path = make_temp_directory / "folder_to_zip.zip"
        assert archive_path.exists()

    def test_execute_creates_zip_with_custom_name(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет создание архива с указанным именем
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        folder = make_temp_directory / "folder_to_zip"
        folder.mkdir()
        (folder / "file.txt").write_text("content")

        custom_archive = make_temp_directory / "custom_name.zip"

        monkeypatch.chdir(make_temp_directory)
        zip_obj = Zip()

        tokens = argparse.Namespace(paths=[str(folder), str(custom_archive)])
        zip_obj.execute(tokens)

        assert custom_archive.exists()

    def test_execute_adds_zip_extension_if_missing(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет добавление расширения .zip
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        folder = make_temp_directory / "folder_to_zip"
        folder.mkdir()
        (folder / "file.txt").write_text("content")

        archive_without_ext = make_temp_directory / "archive"

        monkeypatch.chdir(make_temp_directory)
        zip_obj = Zip()

        tokens = argparse.Namespace(
            paths=[str(folder), str(archive_without_ext)]
        )
        zip_obj.execute(tokens)

        assert (make_temp_directory / "archive.zip").exists()

    def test_execute_with_nested_files(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет архивацию папки с вложенными файлами
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        folder = make_temp_directory / "folder_to_zip"
        folder.mkdir()
        subdir = folder / "subdir"
        subdir.mkdir()
        (folder / "file1.txt").write_text("content1")
        (subdir / "file2.txt").write_text("content2")

        monkeypatch.chdir(make_temp_directory)
        zip_obj = Zip()

        tokens = argparse.Namespace(paths=[str(folder)])
        zip_obj.execute(tokens)

        archive_path = make_temp_directory / "folder_to_zip.zip"
        assert archive_path.exists()

        with zipfile.ZipFile(archive_path, "r") as zf:
            names = zf.namelist()
            assert any("file1.txt" in n for n in names)
            assert any("file2.txt" in n for n in names)

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
        zip_obj = Zip()

        tokens = argparse.Namespace(paths=[str(folder)])
        zip_obj.execute(tokens)

        archive_path = make_temp_directory / "empty_folder.zip"
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
        zip_obj = Zip()

        tokens = argparse.Namespace(paths=[])

        with pytest.raises(ShellError):
            zip_obj.execute(tokens)

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
        zip_obj = Zip()

        tokens = argparse.Namespace(paths=[str(nonexistent)])

        with pytest.raises(PathNotFoundError):
            zip_obj.execute(tokens)

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
        file.write_text("content")

        monkeypatch.chdir(make_temp_directory)
        zip_obj = Zip()

        tokens = argparse.Namespace(paths=[str(file)])

        with pytest.raises(NotADirectoryError):
            zip_obj.execute(tokens)

    def test_zip_method_creates_valid_archive(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет что _zip создаёт валидный архив
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        folder = make_temp_directory / "folder_to_zip"
        folder.mkdir()
        (folder / "file.txt").write_text("test content")

        archive_path = make_temp_directory / "archive.zip"

        monkeypatch.chdir(make_temp_directory)
        zip_obj = Zip()

        zip_obj._zip(str(folder), str(archive_path))

        with zipfile.ZipFile(archive_path, "r") as zf:
            names = zf.namelist()
            assert "file.txt" in names

    def test_execute_with_relative_path(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет архивацию с относительным путём
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        folder = make_temp_directory / "folder_to_zip"
        folder.mkdir()
        (folder / "file.txt").write_text("content")

        monkeypatch.chdir(make_temp_directory)
        zip_obj = Zip()

        tokens = argparse.Namespace(paths=["folder_to_zip"])
        zip_obj.execute(tokens)

        archive_path = make_temp_directory / "folder_to_zip.zip"
        assert archive_path.exists()

    def test_execute_archive_contains_file_hierarchy(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет что архив сохраняет иерархию файлов
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        folder = make_temp_directory / "folder_to_zip"
        folder.mkdir()
        (folder / "file1.txt").write_text("content1")

        subdir1 = folder / "subdir1"
        subdir1.mkdir()
        (subdir1 / "file2.txt").write_text("content2")

        subdir2 = folder / "subdir2"
        subdir2.mkdir()
        (subdir2 / "file3.txt").write_text("content3")

        monkeypatch.chdir(make_temp_directory)
        zip_obj = Zip()

        tokens = argparse.Namespace(paths=[str(folder)])
        zip_obj.execute(tokens)

        archive_path = make_temp_directory / "folder_to_zip.zip"

        with zipfile.ZipFile(archive_path, "r") as zf:
            names = zf.namelist()
            assert "file1.txt" in names
            assert any("subdir1" in n for n in names)
            assert any("file2.txt" in n for n in names)
            assert any("subdir2" in n for n in names)
            assert any("file3.txt" in n for n in names)

    def test_execute_uses_deflate_compression(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет что используется сжатие DEFLATE
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        folder = make_temp_directory / "folder_to_zip"
        folder.mkdir()
        (folder / "file.txt").write_text("content" * 1000)

        monkeypatch.chdir(make_temp_directory)
        zip_obj = Zip()

        tokens = argparse.Namespace(paths=[str(folder)])
        zip_obj.execute(tokens)

        archive_path = make_temp_directory / "folder_to_zip.zip"

        with zipfile.ZipFile(archive_path, "r") as zf:
            for info in zf.filelist:
                assert info.compress_type == zipfile.ZIP_DEFLATED

    def test_execute_multiple_nested_directories(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет архивацию с глубокой вложенностью директорий
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        folder = make_temp_directory / "folder_to_zip"
        folder.mkdir()

        deep_dir = folder / "a" / "b" / "c" / "d" / "e"
        deep_dir.mkdir(parents=True)
        (deep_dir / "file.txt").write_text("deep content")

        monkeypatch.chdir(make_temp_directory)
        zip_obj = Zip()

        tokens = argparse.Namespace(paths=[str(folder)])
        zip_obj.execute(tokens)

        archive_path = make_temp_directory / "folder_to_zip.zip"

        with zipfile.ZipFile(archive_path, "r") as zf:
            names = zf.namelist()
            assert any("a/b/c/d/e/file.txt" in n for n in names)

    def test_execute_creates_archive_in_specified_location(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет что архив создаётся в правильном месте
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        folder = make_temp_directory / "folder_to_zip"
        folder.mkdir()
        (folder / "file.txt").write_text("content")

        archive_dir = make_temp_directory / "archives"
        archive_dir.mkdir()
        archive_path = archive_dir / "my_archive.zip"

        monkeypatch.chdir(make_temp_directory)
        zip_obj = Zip()

        tokens = argparse.Namespace(paths=[str(folder), str(archive_path)])
        zip_obj.execute(tokens)

        assert archive_path.exists()
        assert not (make_temp_directory / "folder_to_zip.zip").exists()

    def test_execute_preserves_file_contents(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет что содержимое файлов сохраняется
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        folder = make_temp_directory / "folder_to_zip"
        folder.mkdir()

        content = "Hello, World! 12345 !@#$%^&*()"
        (folder / "file.txt").write_text(content)

        monkeypatch.chdir(make_temp_directory)
        zip_obj = Zip()

        tokens = argparse.Namespace(paths=[str(folder)])
        zip_obj.execute(tokens)

        archive_path = make_temp_directory / "folder_to_zip.zip"

        with zipfile.ZipFile(archive_path, "r") as zf:
            extracted_content = zf.read("file.txt").decode("utf-8")
            assert extracted_content == content
