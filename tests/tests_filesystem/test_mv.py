import argparse
import os
from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch

from src.filesystem.mv import Mv
from src.utils.errors import MovingError, PathNotFoundError, ShellError


class TestsMv:
    """Тесты для команды mv"""

    def test_mv_init(self) -> None:
        """
        Проверяет инициализацию команды
        """
        mv = Mv()
        assert "src/history/.history" in mv._history_path
        assert "src/history/.trash" in mv._trash_path
        assert "src/history/.undo_history" in mv._undo_history_path

    def test_mv_file(self, make_temp_directory: Path) -> None:
        """
        Проверяет перемещение файла
        :param make_temp_directory: Фикстура для временных директорий
        """
        source = make_temp_directory / "source.txt"
        source.write_text("content")
        destination = make_temp_directory / "destination.txt"

        tokens = argparse.Namespace(paths=[str(source), str(destination)])
        Mv().execute(tokens)

        assert not source.exists()
        assert destination.exists()
        assert destination.read_text() == "content"

    def test_mv_file_to_directory(self, make_temp_directory: Path) -> None:
        """
        Проверяет перемещение файла в директорию
        :param make_temp_directory: Фикстура для временных директорий
        """
        source = make_temp_directory / "source.txt"
        source.write_text("content")
        destination_dir = make_temp_directory / "destdir"
        destination_dir.mkdir()

        tokens = argparse.Namespace(paths=[str(source), str(destination_dir)])
        Mv().execute(tokens)

        moved_file = destination_dir / "source.txt"
        assert not source.exists()
        assert moved_file.exists()
        assert moved_file.read_text() == "content"

    def test_mv_rename_file(self, make_temp_directory: Path) -> None:
        """
        Проверяет переименование файла
        :param make_temp_directory: Фикстура для временных директорий
        """
        source = make_temp_directory / "old.txt"
        source.write_text("content")
        destination = make_temp_directory / "new.txt"

        tokens = argparse.Namespace(paths=[str(source), str(destination)])
        Mv().execute(tokens)

        assert not source.exists()
        assert destination.exists()

    def test_mv_multiple_files(self, make_temp_directory: Path) -> None:
        """
        Проверяет перемещение нескольких файлов
        :param make_temp_directory: Фикстура для временных директорий
        """
        file1 = make_temp_directory / "file1.txt"
        file2 = make_temp_directory / "file2.txt"
        dest_dir = make_temp_directory / "destdir"

        file1.write_text("content1")
        file2.write_text("content2")
        dest_dir.mkdir()

        tokens = argparse.Namespace(
            paths=[str(file1), str(file2), str(dest_dir)]
        )
        Mv().execute(tokens)

        assert not file1.exists()
        assert not file2.exists()
        assert (dest_dir / "file1.txt").exists()
        assert (dest_dir / "file2.txt").exists()

    def test_mv_no_paths_raises_error(self) -> None:
        """
        Проверяет ошибку при пустом списке путей
        :raises PathNotFoundError: При пустом списке путей
        """
        tokens = argparse.Namespace(paths=[])
        with pytest.raises(PathNotFoundError) as exc_info:
            Mv().execute(tokens)
        assert "Отсутствует путь файла" in str(exc_info.value)

    def test_mv_one_path_raises_error(self, make_temp_directory: Path) -> None:
        """
        Проверяет ошибку при одном пути
        :param make_temp_directory: Фикстура для временных директорий
        :raises PathNotFoundError: При недостаточном количестве путей
        """
        source = make_temp_directory / "source.txt"
        source.write_text("content")

        tokens = argparse.Namespace(paths=[str(source)])
        with pytest.raises(PathNotFoundError) as exc_info:
            Mv().execute(tokens)
        assert "Отсутствует путь файла" in str(exc_info.value)

    def test_mv_nonexistent_source(self, make_temp_directory: Path) -> None:
        """
        Проверяет ошибку при несуществующем источнике
        :param make_temp_directory: Фикстура для временных директорий
        :raises ShellError: При несуществующем источнике
        """
        source = make_temp_directory / "nonexistent.txt"
        destination = make_temp_directory / "destination.txt"

        tokens = argparse.Namespace(paths=[str(source), str(destination)])
        with pytest.raises(ShellError):
            Mv().execute(tokens)

    def test_mv_system_file_raises_error(self) -> None:
        """
        Проверяет ошибку при попытке переместить системный файл
        :raises MovingError: При попытке переместить системный файл
        """
        undo_path = os.path.join(os.getcwd(), "src/history/.undo_history")
        dest = os.path.join(os.getcwd(), "somewhere.txt")

        tokens = argparse.Namespace(paths=[undo_path, dest])
        with pytest.raises(MovingError) as exc_info:
            Mv().execute(tokens)
        assert "системные файлы" in str(exc_info.value)

    def test_mv_no_read_permission_raises_error(
        self, make_temp_directory: Path
    ) -> None:
        """
        Проверяет ошибку при отсутствии прав чтения
        :param make_temp_directory: Фикстура для временных директорий
        :raises MovingError: При отсутствии прав чтения
        """
        source = make_temp_directory / "source.txt"
        source.write_text("content")
        source.chmod(0o000)

        destination = make_temp_directory / "destination.txt"

        try:
            tokens = argparse.Namespace(paths=[str(source), str(destination)])
            with pytest.raises(MovingError) as exc_info:
                Mv().execute(tokens)
            assert "Нет прав доступа" in str(exc_info.value)
        finally:
            source.chmod(0o644)

    def test_mv_no_write_permission_on_target_raises_error(
        self, make_temp_directory: Path
    ) -> None:
        """
        Проверяет ошибку при отсутствии прав записи на целевой директории
        :param make_temp_directory: Фикстура для временных директорий
        :raises MovingError: При отсутствии прав записи
        """
        source = make_temp_directory / "source.txt"
        source.write_text("content")

        readonly_dir = make_temp_directory / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o555)

        destination = readonly_dir / "destination.txt"

        try:
            tokens = argparse.Namespace(paths=[str(source), str(destination)])
            with pytest.raises(MovingError) as exc_info:
                Mv().execute(tokens)
            assert "Нет прав доступа" in str(exc_info.value)
        finally:
            readonly_dir.chmod(0o755)

    def test_mv_relative_paths(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
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

        tokens = argparse.Namespace(paths=["source.txt", "destination.txt"])
        Mv().execute(tokens)

        assert not source.exists()
        assert destination.exists()

    def test_mv_saves_undo_info(self, make_temp_directory: Path) -> None:
        """
        Проверяет сохранение информации для отмены
        :param make_temp_directory: Фикстура для временных директорий
        """
        source = make_temp_directory / "source.txt"
        source.write_text("content")
        destination = make_temp_directory / "destination.txt"

        tokens = argparse.Namespace(paths=[str(source), str(destination)])
        Mv().execute(tokens)

        undo_path = Path("src/history/.undo_history")
        if undo_path.exists():
            content = undo_path.read_text()
            assert "mv" in content

    def test_mv_directory(self, make_temp_directory: Path) -> None:
        """
        Проверяет перемещение директории
        :param make_temp_directory: Фикстура для временных директорий
        """
        source_dir = make_temp_directory / "sourcedir"
        source_dir.mkdir()
        (source_dir / "file.txt").write_text("content")

        destination = make_temp_directory / "destdir"

        tokens = argparse.Namespace(paths=[str(source_dir), str(destination)])
        Mv().execute(tokens)

        assert not source_dir.exists()
        assert destination.exists()
        assert (destination / "file.txt").exists()

    def test_mv_with_spaces_in_path(self, make_temp_directory: Path) -> None:
        """
        Проверяет перемещение файла с пробелами в имени
        :param make_temp_directory: Фикстура для временных директорий
        """
        source = make_temp_directory / "file with spaces.txt"
        source.write_text("content")
        destination = make_temp_directory / "new file with spaces.txt"

        tokens = argparse.Namespace(paths=[str(source), str(destination)])
        Mv().execute(tokens)

        assert not source.exists()
        assert destination.exists()

    def test_mv_absolute_paths(self, make_temp_directory: Path) -> None:
        """
        Проверяет использование абсолютных путей
        :param make_temp_directory: Фикстура для временных директорий
        """
        source = make_temp_directory / "source.txt"
        source.write_text("content")
        destination = make_temp_directory / "destination.txt"

        tokens = argparse.Namespace(
            paths=[str(source.resolve()), str(destination.resolve())]
        )
        Mv().execute(tokens)

        assert not source.exists()
        assert destination.exists()
