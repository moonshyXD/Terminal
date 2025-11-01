import argparse
import os
from pathlib import Path

import pytest
from _pytest.capture import CaptureFixture
from _pytest.monkeypatch import MonkeyPatch

from src.history.undo import Undo
from src.utils.errors import CommandNotFoundError, PathNotFoundError, UndoError


class TestsUndo:
    """Тесты для Undo"""

    def test_undo_init(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет инициализацию Undo
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        monkeypatch.chdir(make_temp_directory)
        undo = Undo()

        assert undo.undo_history_path is not None
        assert "src/history/.undo_history" in undo.undo_history_path
        assert undo.undo_trash_path is not None
        assert "src/history/.trash" in undo.undo_trash_path
        assert undo.parser is not None
        assert "cp" in undo.COMMANDS
        assert "mv" in undo.COMMANDS
        assert "rm" in undo.COMMANDS

    def test_execute_no_commands_raises_error(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет ошибку при отсутствии команд для отмены
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        :raises UndoError: При отсутствии команд
        """
        undo_history = (
            make_temp_directory / "src" / "history" / ".undo_history"
        )
        undo_history.write_text("")

        monkeypatch.chdir(make_temp_directory)
        undo = Undo()

        tokens = argparse.Namespace()
        with pytest.raises(UndoError) as exc_info:
            undo.execute(tokens)
        assert "Команды для отмены не найдены" in str(exc_info.value)

    def test_get_last_command_returns_string(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет возврат последней команды
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        undo_history = (
            make_temp_directory / "src" / "history" / ".undo_history"
        )
        undo_history.write_text("cp source dest\nmv old new\n")

        monkeypatch.chdir(make_temp_directory)
        undo = Undo()

        result = undo._get_last_command()

        assert "mv old new" in result

    def test_get_last_command_file_not_found(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет ошибку при отсутствии файла истории
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        :raises CommandNotFoundError: При отсутствии файла
        """
        monkeypatch.chdir(make_temp_directory)
        undo = Undo()
        if os.path.exists(undo.undo_history_path):
            os.remove(undo.undo_history_path)

        with pytest.raises(CommandNotFoundError):
            undo._get_last_command()

    def test_get_last_command_group_returns_mv_commands(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет получение группы команд mv
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        undo_history = (
            make_temp_directory / "src" / "history" / ".undo_history"
        )
        undo_history.write_text(
            "cp source dest\nmv file1 dest1\nmv file2 dest2\n"
        )

        monkeypatch.chdir(make_temp_directory)
        undo = Undo()

        result = undo._get_last_command_group()

        assert len(result) == 2
        assert "mv file1 dest1" in result[0]
        assert "mv file2 dest2" in result[1]

    def test_get_last_command_group_returns_rm_commands(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет получение группы команд rm
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        undo_history = (
            make_temp_directory / "src" / "history" / ".undo_history"
        )
        undo_history.write_text(
            "cp source dest\nrm file1\nrm file2\nrm file3\n"
        )

        monkeypatch.chdir(make_temp_directory)
        undo = Undo()

        result = undo._get_last_command_group()

        assert len(result) == 3

    def test_get_last_command_group_returns_empty_for_cp(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет что группа пуста для cp
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        undo_history = (
            make_temp_directory / "src" / "history" / ".undo_history"
        )
        undo_history.write_text("cp source dest\n")

        monkeypatch.chdir(make_temp_directory)
        undo = Undo()

        result = undo._get_last_command_group()

        assert len(result) == 0

    def test_remove_last_lines_removes_correctly(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет удаление последних строк
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        undo_history = (
            make_temp_directory / "src" / "history" / ".undo_history"
        )
        undo_history.write_text("goose1\ngoose2\ngoose3\ngoose4\n")

        monkeypatch.chdir(make_temp_directory)
        undo = Undo()

        undo._remove_last_lines(2)

        content = undo_history.read_text()
        assert "goose1" in content
        assert "goose2" in content
        assert "goose3" not in content
        assert "goose4" not in content

    def test_undo_cp_removes_file(
        self,
        make_temp_directory: Path,
        capsys: CaptureFixture[str],
        monkeypatch: MonkeyPatch,
    ) -> None:
        """
        Проверяет отмену cp для файла
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        :param monkeypatch: Фикстура для изменения окружения
        """
        file_to_remove = make_temp_directory / "copied_file.txt"
        file_to_remove.write_text("goose")

        monkeypatch.chdir(make_temp_directory)
        undo = Undo()

        tokens = argparse.Namespace(paths=[str(file_to_remove)])
        undo._undo_cp(tokens)

        assert not file_to_remove.exists()

    def test_undo_cp_removes_directory(
        self,
        make_temp_directory: Path,
        capsys: CaptureFixture[str],
        monkeypatch: MonkeyPatch,
    ) -> None:
        """
        Проверяет отмену cp для директории
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        :param monkeypatch: Фикстура для изменения окружения
        """
        dir_to_remove = make_temp_directory / "copied_dir"
        dir_to_remove.mkdir()
        (dir_to_remove / "file.txt").write_text("goose")

        monkeypatch.chdir(make_temp_directory)
        undo = Undo()

        tokens = argparse.Namespace(paths=[str(dir_to_remove)])
        undo._undo_cp(tokens)

        assert not dir_to_remove.exists()

    def test_undo_mv_restores_file(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет отмену mv
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        file_in_new = make_temp_directory / "new_location" / "file.txt"
        file_in_new.parent.mkdir()
        file_in_new.write_text("goose")

        original_location = make_temp_directory / "original"
        original_location.mkdir()

        monkeypatch.chdir(make_temp_directory)
        undo = Undo()

        tokens = argparse.Namespace(
            paths=[str(file_in_new), str(original_location / "file.txt")]
        )
        undo._undo_mv(tokens)

        assert (original_location / "file.txt").exists()
        assert not file_in_new.exists()

    def test_undo_rm_restores_file(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет отмену rm
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        trash = make_temp_directory / "src" / "history" / ".trash"
        trash.mkdir(parents=True, exist_ok=True)

        deleted_file = trash / "deleted.txt"
        deleted_file.write_text("goose")

        restore_dir = make_temp_directory / "restore"
        restore_dir.mkdir()

        monkeypatch.chdir(make_temp_directory)
        undo = Undo()

        tokens = argparse.Namespace(paths=["deleted.txt", str(restore_dir)])
        undo._undo_rm(tokens)

        assert (restore_dir / "deleted.txt").exists()
        assert not deleted_file.exists()

    def test_add_undo_history_appends_command(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет добавление команды в историю отмены
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        undo_history = (
            make_temp_directory / "src" / "history" / ".undo_history"
        )
        undo_history.write_text("cp source dest\n")

        monkeypatch.chdir(make_temp_directory)
        undo = Undo()

        undo.add_undo_history("mv file1 file2\n")

        content = undo_history.read_text()
        assert "cp source dest" in content
        assert "mv file1 file2" in content

    def test_clear_undo_history_clears_file(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет очистку истории отмены
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        undo_history = (
            make_temp_directory / "src" / "history" / ".undo_history"
        )
        undo_history.write_text("cp source dest\nmv file1 file2\n")

        trash = make_temp_directory / "src" / "history" / ".trash"
        trash.mkdir(parents=True, exist_ok=True)
        (trash / "file.txt").write_text("goose")

        monkeypatch.chdir(make_temp_directory)
        undo = Undo()

        undo.clear_undo_history()

        assert undo_history.read_text() == ""
        assert trash.exists()

    def test_execute_with_mv_command(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет выполнение отмены для команды mv
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        file_in_new = make_temp_directory / "new" / "file.txt"
        file_in_new.parent.mkdir()
        file_in_new.write_text("goose")

        original = make_temp_directory / "original"
        original.mkdir()

        undo_history = (
            make_temp_directory / "src" / "history" / ".undo_history"
        )
        undo_history.write_text(
            f"mv {str(file_in_new)} {str(original)}/file.txt\n"
        )

        monkeypatch.chdir(make_temp_directory)
        undo = Undo()

        tokens = argparse.Namespace()
        undo.execute(tokens)

        assert (original / "file.txt").exists()

    def test_get_last_command_group_file_not_found(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет ошибку при отсутствии файла в _get_last_command_group
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        :raises PathNotFoundError: При отсутствии файла
        """
        monkeypatch.chdir(make_temp_directory)
        undo = Undo()
        if os.path.exists(undo.undo_history_path):
            os.remove(undo.undo_history_path)

        with pytest.raises(PathNotFoundError):
            undo._get_last_command_group()

    def test_remove_last_lines_file_not_found(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет ошибку при отсутствии файла в _remove_last_lines
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        :raises PathNotFoundError: При отсутствии файла
        """
        monkeypatch.chdir(make_temp_directory)
        undo = Undo()
        if os.path.exists(undo.undo_history_path):
            os.remove(undo.undo_history_path)

        with pytest.raises(PathNotFoundError):
            undo._remove_last_lines(1)
