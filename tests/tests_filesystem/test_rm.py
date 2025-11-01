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
        """Проверяет инициализацию команды"""
        rm = Rm()
        assert "src/history/.trash" in rm._trash_path
        assert "src/history/.undo_history" in rm._undo_history_path

    def test_rm_delete_file(self, make_temp_directory: Path) -> None:
        """Проверяет удаление файла в корзину"""
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
        """Проверяет удаление директории с подтверждением"""
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
        """Проверяет отмену удаления директории"""
        dir_to_remove = make_temp_directory / "testdir"
        dir_to_remove.mkdir()

        rm = Rm()

        tokens = argparse.Namespace(paths=[str(dir_to_remove)], recursive=True)

        with patch("builtins.input", return_value="n"):
            with patch("builtins.print"):
                rm.execute(tokens)

        assert dir_to_remove.exists()

    def test_rm_nonexistent_file_raises_error(
        self, make_temp_directory: Path
    ) -> None:
        """Проверяет ошибку при несуществующем файле"""
        rm = Rm()
        tokens = argparse.Namespace(
            paths=[str(make_temp_directory / "nonexistent.txt")],
            recursive=False,
        )
        with pytest.raises(ShellError):
            rm.execute(tokens)

    def test_rm_saves_undo_info(self, make_temp_directory: Path) -> None:
        """Проверяет сохранение информации для отмены"""
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
        """Проверяет удаление файла по относительному пути"""
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
        """Проверяет удаление файла по абсолютному пути"""
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
        """Проверяет удаление нескольких файлов"""
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

    def test_rm_duplicate_filenames(self, make_temp_directory: Path) -> None:
        """Проверяет создание уникальных имён при конфликтах"""
        file1 = make_temp_directory / "file.txt"
        file1.write_text("content1")

        trash_path = make_temp_directory / "src" / "history" / ".trash"
        trash_path.mkdir(parents=True, exist_ok=True)
        (trash_path / "file.txt").write_text("already_in_trash")

        rm = Rm()
        rm._trash_path = str(trash_path)

        tokens = argparse.Namespace(paths=[str(file1)], recursive=False)
        rm.execute(tokens)

        assert not file1.exists()
        assert (trash_path / "file.txt").exists()
        assert (trash_path / "file_1.txt").exists()

    def test_rm_file_not_directory_raises_error(
        self, make_temp_directory: Path
    ) -> None:
        """Проверяет ошибку при попытке удалить файл с флагом -r"""
        file = make_temp_directory / "file.txt"
        file.write_text("content")
        trash_path = make_temp_directory / "src" / "history" / ".trash"
        trash_path.mkdir(parents=True, exist_ok=True)

        rm = Rm()
        rm._trash_path = str(trash_path)

        tokens = argparse.Namespace(paths=[str(file)], recursive=True)

        with pytest.raises(DeletingError):
            rm.execute(tokens)
