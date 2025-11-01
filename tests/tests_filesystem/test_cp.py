import argparse
from pathlib import Path

import pytest

from src.filesystem.cp import Cp
from src.utils.errors import PathNotFoundError, ShellError


class TestsCp:
    """Тесты для команды cp"""

    def test_cp_init(self) -> None:
        """
        Проверяет инициализацию команды
        """
        cp = Cp()
        assert cp._command == "cp"
        assert "src/history/.undo_history" in cp.undo_history_path

    def test_cp_file_to_file(self, make_temp_directory: Path) -> None:
        """
        Проверяет копирование файла в файл
        :param make_temp_directory: Фикстура для временных директорий
        """
        source = make_temp_directory / "source.txt"
        source.write_text("content")
        destination = make_temp_directory / "destination.txt"

        tokens = argparse.Namespace(
            paths=[str(source), str(destination)], recursive=False
        )
        Cp().execute(tokens)

        assert destination.exists()
        assert destination.read_text() == "content"
        assert source.exists()

    def test_cp_directory_recursive(self, make_temp_structure: Path) -> None:
        """
        Проверяет рекурсивное копирование директории
        :param make_temp_structure: Фикстура с тестовой структурой
        """
        destination = make_temp_structure.parent / "copied"

        tokens = argparse.Namespace(
            paths=[str(make_temp_structure), str(destination)], recursive=True
        )
        Cp().execute(tokens)

        assert (destination / "temp_directory").exists()
        assert (destination / "temp_directory" / "file1.txt").exists()
        assert (destination / "temp_directory" / "file2.txt").exists()

    def test_cp_no_paths_raises_error(self) -> None:
        """
        Проверяет ошибку при отсутствии путей
        :raises PathNotFoundError: При отсутствии путей
        """
        tokens = argparse.Namespace(paths=[], recursive=False)
        with pytest.raises(PathNotFoundError) as exc_info:
            Cp().execute(tokens)
        assert "Отсутствует путь файла" in str(exc_info.value)

    def test_cp_one_path_raises_error(self, make_temp_directory: Path) -> None:
        """
        Проверяет ошибку при одном пути
        :param make_temp_directory: Фикстура для временных директорий
        :raises PathNotFoundError: При недостаточном количестве путей
        """
        source = make_temp_directory / "source.txt"
        source.write_text("content")

        tokens = argparse.Namespace(paths=[str(source)], recursive=False)
        with pytest.raises(PathNotFoundError) as exc_info:
            Cp().execute(tokens)
        assert "Отсутствует путь файла" in str(exc_info.value)

    def test_cp_nonexistent_source(self, make_temp_directory: Path) -> None:
        """
        Проверяет ошибку при несуществующем источнике
        :param make_temp_directory: Фикстура для временных директорий
        :raises ShellError: При несуществующем источнике
        """
        source = make_temp_directory / "nonexistent.txt"
        destination = make_temp_directory / "destination.txt"

        tokens = argparse.Namespace(
            paths=[str(source), str(destination)], recursive=False
        )
        with pytest.raises(ShellError):
            Cp().execute(tokens)

    def test_cp_directory_without_recursive_raises_error(
        self, make_temp_structure: Path
    ) -> None:
        """
        Проверяет ошибку при копировании директории без -r
        :param make_temp_structure: Фикстура с тестовой структурой
        :raises ShellError: При попытке копировать директорию без флага
        """
        destination = make_temp_structure.parent / "copied"

        tokens = argparse.Namespace(
            paths=[str(make_temp_structure), str(destination)], recursive=False
        )
        with pytest.raises(ShellError):
            Cp().execute(tokens)

    def test_cp_to_nonexistent_directory_raises_error(
        self, make_temp_directory: Path
    ) -> None:
        """
        Проверяет ошибку при несуществующей целевой директории
        :param make_temp_directory: Фикстура для временных директорий
        :raises ShellError: При несуществующей целевой директории
        """
        source = make_temp_directory / "source.txt"
        source.write_text("content")
        destination = make_temp_directory / "nonexistent" / "destination.txt"

        tokens = argparse.Namespace(
            paths=[str(source), str(destination)], recursive=False
        )
        with pytest.raises(ShellError):
            Cp().execute(tokens)

    def test_cp_overwrites_existing_file(
        self, make_temp_directory: Path
    ) -> None:
        """
        Проверяет перезапись существующего файла
        :param make_temp_directory: Фикстура для временных директорий
        """
        source = make_temp_directory / "source.txt"
        source.write_text("new")
        destination = make_temp_directory / "destination.txt"
        destination.write_text("old")

        tokens = argparse.Namespace(
            paths=[str(source), str(destination)], recursive=False
        )
        Cp().execute(tokens)

        assert destination.read_text() == "new"

    def test_cp_saves_undo_info_file(self, make_temp_directory: Path) -> None:
        """
        Проверяет сохранение информации для отмены
        :param make_temp_directory: Фикстура для временных директорий
        """
        source = make_temp_directory / "source.txt"
        source.write_text("content")
        destination = make_temp_directory / "destination.txt"

        tokens = argparse.Namespace(
            paths=[str(source), str(destination)], recursive=False
        )
        Cp().execute(tokens)

        undo_path = Path("src/history/.undo_history")
        if undo_path.exists():
            content = undo_path.read_text()
            assert "cp" in content
            assert str(destination.resolve()) in content

    def test_cp_saves_undo_info_directory(
        self, make_temp_structure: Path
    ) -> None:
        """
        Проверяет сохранение информации для отмены директории
        :param make_temp_structure: Фикстура с тестовой структурой
        """
        destination = make_temp_structure.parent / "copied"

        tokens = argparse.Namespace(
            paths=[str(make_temp_structure), str(destination)], recursive=True
        )
        Cp().execute(tokens)

        undo_path = Path("src/history/.undo_history")
        if undo_path.exists():
            content = undo_path.read_text()
            assert "cp" in content

    def test_cp_relative_paths(
        self, make_temp_directory: Path, monkeypatch
    ) -> None:
        """
        Проверяет работу с относительными путями
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        source = make_temp_directory / "source.txt"
        source.write_text("content")
        destination = make_temp_directory / "destination.txt"

        monkeypatch.chdir(make_temp_directory)

        tokens = argparse.Namespace(
            paths=["source.txt", "destination.txt"], recursive=False
        )
        Cp().execute(tokens)

        assert destination.exists()
        assert destination.read_text() == "content"

    def test_cp_absolute_paths(self, make_temp_directory: Path) -> None:
        """
        Проверяет работу с абсолютными путями
        :param make_temp_directory: Фикстура для временных директорий
        """
        source = make_temp_directory / "source.txt"
        source.write_text("content")
        destination = make_temp_directory / "destination.txt"

        tokens = argparse.Namespace(
            paths=[str(source.resolve()), str(destination.resolve())],
            recursive=False,
        )
        Cp().execute(tokens)

        assert destination.exists()
        assert destination.read_text() == "content"
        assert source.exists()

    def test_cp_directory_with_trailing_slash(
        self, make_temp_structure: Path
    ) -> None:
        """
        Проверяет копирование директории с / в конце
        :param make_temp_structure: Фикстура с тестовой структурой
        """
        destination = make_temp_structure.parent / "copied"
        source_with_slash = str(make_temp_structure) + "/"

        tokens = argparse.Namespace(
            paths=[source_with_slash, str(destination)], recursive=True
        )
        Cp().execute(tokens)

        assert (destination / "temp_directory").exists()

    def test_cp_empty_file(self, make_temp_directory: Path) -> None:
        """
        Проверяет копирование пустого файла
        :param make_temp_directory: Фикстура для временных директорий
        """
        source = make_temp_directory / "empty.txt"
        source.write_text("")
        destination = make_temp_directory / "copy.txt"

        tokens = argparse.Namespace(
            paths=[str(source), str(destination)], recursive=False
        )
        Cp().execute(tokens)

        assert destination.exists()
        assert destination.read_text() == ""
