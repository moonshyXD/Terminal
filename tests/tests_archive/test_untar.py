import argparse
import tarfile
from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch

from src.archive.untar import Untar
from src.utils.errors import NotAFileError, PathNotFoundError, ShellError


class TestsUntar:
    """Тесты для Untar"""

    def test_untar_init(self) -> None:
        """
        Проверяет инициализацию Untar
        """
        untar = Untar()

        assert isinstance(untar, Untar)

    def test_execute_extracts_tar_gz_archive(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет распаковку tar.gz архива
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        # Создаём архив
        source_dir = make_temp_directory / "source"
        source_dir.mkdir()
        (source_dir / "file.txt").write_text("content")

        archive_path = make_temp_directory / "archive.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(str(source_dir), arcname="source")

        # Распаковываем
        extract_dir = make_temp_directory / "extract"
        extract_dir.mkdir()

        monkeypatch.chdir(extract_dir)
        untar = Untar()

        tokens = argparse.Namespace(paths=[str(archive_path)])
        untar.execute(tokens)

        assert (extract_dir / "source").exists()
        assert (extract_dir / "source" / "file.txt").exists()

    def test_execute_extracts_to_current_directory(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет что распаковка происходит в текущую директорию
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        source_dir = make_temp_directory / "source"
        source_dir.mkdir()
        (source_dir / "file1.txt").write_text("content1")
        (source_dir / "file2.txt").write_text("content2")

        archive_path = make_temp_directory / "archive.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(str(source_dir), arcname="source")

        extract_dir = make_temp_directory / "extract"
        extract_dir.mkdir()

        monkeypatch.chdir(extract_dir)
        untar = Untar()

        tokens = argparse.Namespace(paths=[str(archive_path)])
        untar.execute(tokens)

        assert any(f.name == "source" for f in extract_dir.iterdir())

    def test_execute_with_nested_files(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет распаковку архива с вложенными файлами
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        source_dir = make_temp_directory / "source"
        source_dir.mkdir()
        subdir = source_dir / "subdir"
        subdir.mkdir()
        (source_dir / "file1.txt").write_text("content1")
        (subdir / "file2.txt").write_text("content2")

        archive_path = make_temp_directory / "archive.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(str(source_dir), arcname="source")

        extract_dir = make_temp_directory / "extract"
        extract_dir.mkdir()

        monkeypatch.chdir(extract_dir)
        untar = Untar()

        tokens = argparse.Namespace(paths=[str(archive_path)])
        untar.execute(tokens)

        assert (extract_dir / "source" / "subdir" / "file2.txt").exists()

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
        untar = Untar()

        tokens = argparse.Namespace(paths=[])

        with pytest.raises(ShellError):
            untar.execute(tokens)

    def test_execute_nonexistent_archive_raises_error(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет ошибку при несуществующем архиве
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        :raises PathNotFoundError: При несуществующем архиве
        """
        nonexistent = make_temp_directory / "nonexistent.tar.gz"

        monkeypatch.chdir(make_temp_directory)
        untar = Untar()

        tokens = argparse.Namespace(paths=[str(nonexistent)])

        with pytest.raises(PathNotFoundError):
            untar.execute(tokens)

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
        untar = Untar()

        tokens = argparse.Namespace(paths=[str(directory)])

        with pytest.raises(NotAFileError):
            untar.execute(tokens)

    def test_untar_method_extracts_correctly(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет что _untar распаковывает архив
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        source_dir = make_temp_directory / "source"
        source_dir.mkdir()
        (source_dir / "file.txt").write_text("test content")

        archive_path = make_temp_directory / "archive.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(str(source_dir), arcname="source")

        extract_dir = make_temp_directory / "extract"
        extract_dir.mkdir()

        monkeypatch.chdir(make_temp_directory)
        untar = Untar()

        untar._untar(str(archive_path), str(extract_dir))

        assert (extract_dir / "source" / "file.txt").exists()
        assert (
            extract_dir / "source" / "file.txt"
        ).read_text() == "test content"

    def test_execute_with_relative_path(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет распаковку с относительным путём
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        source_dir = make_temp_directory / "source"
        source_dir.mkdir()
        (source_dir / "file.txt").write_text("content")

        archive_path = make_temp_directory / "archive.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(str(source_dir), arcname="source")

        extract_dir = make_temp_directory / "extract"
        extract_dir.mkdir()

        monkeypatch.chdir(extract_dir)
        untar = Untar()

        relative_archive = "../archive.tar.gz"
        tokens = argparse.Namespace(paths=[relative_archive])
        untar.execute(tokens)

        assert (extract_dir / "source").exists()

    def test_execute_empty_archive(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет распаковку пустого архива
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        source_dir = make_temp_directory / "source"
        source_dir.mkdir()

        archive_path = make_temp_directory / "archive.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(str(source_dir), arcname="source")

        extract_dir = make_temp_directory / "extract"
        extract_dir.mkdir()

        monkeypatch.chdir(extract_dir)
        untar = Untar()

        tokens = argparse.Namespace(paths=[str(archive_path)])
        untar.execute(tokens)

        assert (extract_dir / "source").exists()

    def test_execute_archive_with_multiple_top_level_items(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет распаковку архива с несколькими элементами на верхнем уровне
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        archive_path = make_temp_directory / "archive.tar.gz"

        # Создаём архив с несколькими элементами
        with tarfile.open(archive_path, "w:gz") as tar:
            file1 = make_temp_directory / "file1.txt"
            file1.write_text("content1")
            tar.add(str(file1), arcname="file1.txt")

            file2 = make_temp_directory / "file2.txt"
            file2.write_text("content2")
            tar.add(str(file2), arcname="file2.txt")

        extract_dir = make_temp_directory / "extract"
        extract_dir.mkdir()

        monkeypatch.chdir(extract_dir)
        untar = Untar()

        tokens = argparse.Namespace(paths=[str(archive_path)])
        untar.execute(tokens)

        assert (extract_dir / "file1.txt").exists()
        assert (extract_dir / "file2.txt").exists()

    def test_untar_method_with_custom_extract_path(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет распаковку в указанную директорию
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        source_dir = make_temp_directory / "source"
        source_dir.mkdir()
        (source_dir / "file.txt").write_text("content")

        archive_path = make_temp_directory / "archive.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(str(source_dir), arcname="source")

        extract_dir = make_temp_directory / "custom_extract"
        extract_dir.mkdir()

        monkeypatch.chdir(make_temp_directory)
        untar = Untar()

        untar._untar(str(archive_path), str(extract_dir))

        assert (extract_dir / "source" / "file.txt").exists()

    def test_execute_preserves_file_contents(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет что содержимое файлов сохраняется
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        source_dir = make_temp_directory / "source"
        source_dir.mkdir()

        content = "Hello, World! 12345 !@#$%^&*()"
        (source_dir / "file.txt").write_text(content)

        archive_path = make_temp_directory / "archive.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(str(source_dir), arcname="source")

        extract_dir = make_temp_directory / "extract"
        extract_dir.mkdir()

        monkeypatch.chdir(extract_dir)
        untar = Untar()

        tokens = argparse.Namespace(paths=[str(archive_path)])
        untar.execute(tokens)

        extracted_content = (extract_dir / "source" / "file.txt").read_text()
        assert extracted_content == content
