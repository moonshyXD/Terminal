import argparse
from pathlib import Path
from unittest.mock import patch

import pytest
from _pytest.monkeypatch import MonkeyPatch

from src.filesystem.rm import Rm
from src.utils.errors import DeletingError, ShellError


class TestsRm:
    """Тесты для команды rm"""

    def test_rm_init(self) -> None:
        """
        Проверяет инициализацию команды
        """
        rm = Rm()
        assert "src/history/.history" in rm._history_path
        assert "src/history/.trash" in rm._trash_path
        assert "src/history/.undo_history" in rm._undo_history_path

    def test_rm_delete_file(self, make_temp_directory: Path) -> None:
        """
        Проверяет удаление файла в корзину
        :param make_temp_directory: Фикстура для временных директорий
        """
        file = make_temp_directory / "file.txt"
        file.write_text("content")
        trash_path = make_temp_directory / "src" / "history" / ".trash"
        trash_path.mkdir(parents=True, exist_ok=True)

        rm = Rm()
        rm._trash_path = str(trash_path)

        tokens = argparse.Namespace(paths=[str(file)], recursive=False)
        rm.execute(tokens)

        assert not file.exists()
        assert (trash_path / "file.txt").exists()

    def test_rm_delete_directory_with_confirmation(
        self, make_temp_directory: Path
    ) -> None:
        """
        Проверяет удаление директории с подтверждением
        :param make_temp_directory: Фикстура для временных директорий
        """
        dir_to_remove = make_temp_directory / "testdir"
        dir_to_remove.mkdir()
        (dir_to_remove / "file.txt").write_text("content")
        trash_path = make_temp_directory / "src" / "history" / ".trash"
        trash_path.mkdir(parents=True, exist_ok=True)

        rm = Rm()
        rm._trash_path = str(trash_path)

        tokens = argparse.Namespace(paths=[str(dir_to_remove)], recursive=True)

        with patch("builtins.input", return_value="y"):
            with patch("builtins.print"):
                rm.execute(tokens)

        assert not dir_to_remove.exists()
        assert (trash_path / "testdir").exists()

    def test_rm_delete_directory_decline(
        self, make_temp_directory: Path
    ) -> None:
        """
        Проверяет отмену удаления директории
        :param make_temp_directory: Фикстура для временных директорий
        """
        dir_to_remove = make_temp_directory / "testdir"
        dir_to_remove.mkdir()

        rm = Rm()

        tokens = argparse.Namespace(paths=[str(dir_to_remove)], recursive=True)

        with patch("builtins.input", return_value="n"):
            with patch("builtins.print"):
                rm.execute(tokens)

        assert dir_to_remove.exists()

    def test_rm_empty_paths_uses_home(self, monkeypatch: MonkeyPatch) -> None:
        """
        Проверяет использование домашней директории при пустых путях
        :param monkeypatch: Фикстура для изменения окружения
        """
        rm = Rm()

        tokens = argparse.Namespace(paths=[], recursive=False)

        with patch.object(rm, "_path_exists"):
            with patch.object(rm, "_is_system_paths"):
                with patch.object(rm, "_is_file"):
                    with patch("shutil.move"):
                        with patch.object(rm, "_save_undo_info"):
                            rm.execute(tokens)

    def test_rm_nonexistent_file_raises_error(
        self, make_temp_directory: Path
    ) -> None:
        """
        Проверяет ошибку при несуществующем файле
        :param make_temp_directory: Фикстура для временных директорий
        :raises ShellError: При несуществующем файле
        """
        rm = Rm()
        tokens = argparse.Namespace(
            paths=[str(make_temp_directory / "nonexistent.txt")],
            recursive=False,
        )
        with pytest.raises(ShellError):
            rm.execute(tokens)

    def test_rm_system_file_raises_error(self) -> None:
        """
        Проверяет ошибку при попытке удалить системный файл
        :raises DeletingError: При попытке удалить системный файл
        """
        rm = Rm()
        import os

        trash_path = os.path.join(os.getcwd(), "src/history/.trash")

        tokens = argparse.Namespace(paths=[trash_path], recursive=False)
        with pytest.raises(DeletingError) as exc_info:
            rm.execute(tokens)
        assert "системные файлы" in str(exc_info.value)

    def test_rm_root_directory_raises_error(self) -> None:
        """
        Проверяет ошибку при попытке удалить корневую директорию
        :raises DeletingError: При попытке удалить корневую директорию
        """
        rm = Rm()

        tokens = argparse.Namespace(paths=["/"], recursive=True)

        with patch.object(rm, "_path_exists"):
            with patch.object(rm, "_is_system_paths"):
                with pytest.raises(DeletingError) as exc_info:
                    rm.execute(tokens)
        assert "корневую директорию" in str(exc_info.value)

    def test_rm_home_directory_raises_error(self) -> None:
        """
        Проверяет ошибку при попытке удалить домашнюю директорию
        :raises DeletingError: При попытке удалить домашнюю директорию
        """
        rm = Rm()
        import os

        home = os.path.expanduser("~")

        tokens = argparse.Namespace(paths=[home], recursive=True)

        with patch.object(rm, "_path_exists"):
            with patch.object(rm, "_is_system_paths"):
                with pytest.raises(DeletingError) as exc_info:
                    rm.execute(tokens)
        assert "корневую директорию" in str(exc_info.value)

    def test_rm_current_directory_raises_error(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет ошибку при попытке удалить текущую директорию
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        :raises DeletingError: При попытке удалить текущую директорию
        """
        monkeypatch.chdir(make_temp_directory)
        rm = Rm()

        tokens = argparse.Namespace(
            paths=[str(make_temp_directory)], recursive=True
        )

        with patch.object(rm, "_path_exists"):
            with patch.object(rm, "_is_system_paths"):
                with pytest.raises(DeletingError) as exc_info:
                    rm.execute(tokens)
        assert "корневую директорию" in str(exc_info.value)

    def test_rm_parent_directory_raises_error(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет ошибку при попытке удалить родительскую директорию
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        :raises DeletingError: При попытке удалить родительскую директорию
        """
        subdir = make_temp_directory / "subdir"
        subdir.mkdir()
        monkeypatch.chdir(subdir)

        rm = Rm()

        tokens = argparse.Namespace(
            paths=[str(make_temp_directory)], recursive=True
        )

        with patch.object(rm, "_path_exists"):
            with patch.object(rm, "_is_system_paths"):
                with patch.object(rm, "_is_directory"):
                    with pytest.raises(DeletingError) as exc_info:
                        rm.execute(tokens)
        assert "Невозможно удалить корневую директорию" in str(exc_info.value)

    def test_rm_file_not_directory_raises_error(
        self, make_temp_directory: Path
    ) -> None:
        """
        Проверяет ошибку при попытке удалить файл с флагом -r
        :param make_temp_directory: Фикстура для временных директорий
        :raises ShellError: При попытке удалить файл как директорию
        """
        file = make_temp_directory / "file.txt"
        file.write_text("content")

        rm = Rm()
        tokens = argparse.Namespace(paths=[str(file)], recursive=True)

        with patch.object(rm, "_path_exists"):
            with patch.object(rm, "_is_system_paths"):
                with pytest.raises(ShellError):
                    rm.execute(tokens)

    def test_rm_saves_undo_info(self, make_temp_directory: Path) -> None:
        """
        Проверяет сохранение информации для отмены
        :param make_temp_directory: Фикстура для временных директорий
        """
        file = make_temp_directory / "file.txt"
        file.write_text("content")
        trash_path = make_temp_directory / "src" / "history" / ".trash"
        trash_path.mkdir(parents=True, exist_ok=True)
        undo_path = make_temp_directory / "src" / "history" / ".undo_history"
        undo_path.touch()

        rm = Rm()
        rm._trash_path = str(trash_path)
        rm._undo_history_path = str(undo_path)

        tokens = argparse.Namespace(paths=[str(file)], recursive=False)
        rm.execute(tokens)

        content = undo_path.read_text()
        assert "rm" in content
        assert "file.txt" in content

    def test_rm_relative_path(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет удаление файла по относительному пути
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        file = make_temp_directory / "file.txt"
        file.write_text("content")
        trash_path = make_temp_directory / "src" / "history" / ".trash"
        trash_path.mkdir(parents=True, exist_ok=True)

        monkeypatch.chdir(make_temp_directory)

        rm = Rm()
        rm._trash_path = str(trash_path)

        tokens = argparse.Namespace(paths=["file.txt"], recursive=False)
        rm.execute(tokens)

        assert not file.exists()

    def test_rm_absolute_path(self, make_temp_directory: Path) -> None:
        """
        Проверяет удаление файла по абсолютному пути
        :param make_temp_directory: Фикстура для временных директорий
        """
        file = make_temp_directory / "file.txt"
        file.write_text("content")
        trash_path = make_temp_directory / "src" / "history" / ".trash"
        trash_path.mkdir(parents=True, exist_ok=True)

        rm = Rm()
        rm._trash_path = str(trash_path)

        tokens = argparse.Namespace(
            paths=[str(file.resolve())], recursive=False
        )
        rm.execute(tokens)

        assert not file.exists()
        assert (trash_path / "file.txt").exists()

    def test_rm_multiple_files(self, make_temp_directory: Path) -> None:
        """
        Проверяет удаление нескольких файлов
        :param make_temp_directory: Фикстура для временных директорий
        """
        file1 = make_temp_directory / "file1.txt"
        file2 = make_temp_directory / "file2.txt"
        file1.write_text("content1")
        file2.write_text("content2")
        trash_path = make_temp_directory / "src" / "history" / ".trash"
        trash_path.mkdir(parents=True, exist_ok=True)

        rm = Rm()
        rm._trash_path = str(trash_path)

        tokens = argparse.Namespace(
            paths=[str(file1), str(file2)], recursive=False
        )
        rm.execute(tokens)

        assert not file1.exists()
        assert not file2.exists()
