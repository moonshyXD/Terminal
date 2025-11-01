import argparse
from pathlib import Path

import pytest
from _pytest.capture import CaptureFixture
from _pytest.monkeypatch import MonkeyPatch

from src.filesystem.ls import Ls
from src.utils.errors import ShellError


class TestsLs:
    """Тесты для команды ls"""

    def test_ls_with_paths_not_detailed(
        self, make_temp_directory: Path, capsys: CaptureFixture[str]
    ) -> None:
        """
        Проверяет вывод с явно указанными путями
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        """
        (make_temp_directory / "file.txt").write_text("content")

        tokens = argparse.Namespace(
            paths=[str(make_temp_directory)], l=False, al=False, all=False
        )
        Ls().execute(tokens)
        captured = capsys.readouterr()

        assert "file.txt" in captured.out

    def test_ls_without_paths_uses_cwd(
        self,
        make_temp_directory: Path,
        capsys: CaptureFixture[str],
        monkeypatch: MonkeyPatch,
    ) -> None:
        """
        Проверяет использование текущей директории
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        :param monkeypatch: Фикстура для изменения окружения
        """
        (make_temp_directory / "file.txt").write_text("content")
        monkeypatch.chdir(make_temp_directory)

        tokens = argparse.Namespace(paths=[], l=False, al=False, all=False)
        Ls().execute(tokens)
        captured = capsys.readouterr()

        assert "file.txt" in captured.out

    def test_ls_not_detailed_with_files(
        self, make_temp_directory: Path, capsys: CaptureFixture[str]
    ) -> None:
        """
        Проверяет простой вывод файлов
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        """
        (make_temp_directory / "file1.txt").write_text("content")
        (make_temp_directory / "file2.txt").write_text("content")

        tokens = argparse.Namespace(
            paths=[str(make_temp_directory)], l=False, al=False, all=False
        )
        Ls().execute(tokens)
        captured = capsys.readouterr()

        assert "file1.txt" in captured.out
        assert "file2.txt" in captured.out
        assert "\033[32m" in captured.out

    def test_ls_not_detailed_with_directories(
        self, make_temp_directory: Path, capsys: CaptureFixture[str]
    ) -> None:
        """
        Проверяет цветное выделение папок в простом виде
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        """
        (make_temp_directory / "subdir").mkdir()
        (make_temp_directory / "file.txt").write_text("content")

        tokens = argparse.Namespace(
            paths=[str(make_temp_directory)], l=False, al=False, all=False
        )
        Ls().execute(tokens)
        captured = capsys.readouterr()

        assert "subdir" in captured.out
        assert "\033[34;42m" in captured.out
        assert "\033[32m" in captured.out

    def test_ls_detailed_view(
        self, make_temp_directory: Path, capsys: CaptureFixture[str]
    ) -> None:
        """
        Проверяет подробный вывод
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        """
        (make_temp_directory / "file.txt").write_text("content")

        tokens = argparse.Namespace(
            paths=[str(make_temp_directory)], l=True, al=False, all=False
        )
        Ls().execute(tokens)
        captured = capsys.readouterr()

        assert "file.txt" in captured.out
        assert "-rw" in captured.out or "drwx" in captured.out

    def test_ls_detailed_with_directory_coloring(
        self, make_temp_directory: Path, capsys: CaptureFixture[str]
    ) -> None:
        """
        Проверяет цветное выделение в подробном виде
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        """
        (make_temp_directory / "subdir").mkdir()

        tokens = argparse.Namespace(
            paths=[str(make_temp_directory)], l=True, al=False, all=False
        )
        Ls().execute(tokens)
        captured = capsys.readouterr()

        assert "subdir" in captured.out
        assert "\033[34;42m" in captured.out

    def test_ls_detailed_with_file_coloring(
        self, make_temp_directory: Path, capsys: CaptureFixture[str]
    ) -> None:
        """
        Проверяет цветное выделение файлов в подробном виде
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        """
        (make_temp_directory / "file.txt").write_text("content")

        tokens = argparse.Namespace(
            paths=[str(make_temp_directory)], l=True, al=False, all=False
        )
        Ls().execute(tokens)
        captured = capsys.readouterr()

        assert "file.txt" in captured.out
        assert "\033[32m" in captured.out

    def test_ls_all_flag_shows_hidden(
        self, make_temp_directory: Path, capsys: CaptureFixture[str]
    ) -> None:
        """
        Проверяет флаг -all для скрытых файлов
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        """
        (make_temp_directory / ".hidden").write_text("hidden")
        (make_temp_directory / "visible.txt").write_text("visible")

        tokens = argparse.Namespace(
            paths=[str(make_temp_directory)], l=False, al=False, all=True
        )
        Ls().execute(tokens)
        captured = capsys.readouterr()

        assert ".hidden" in captured.out
        assert "visible.txt" in captured.out

    def test_ls_without_all_flag_hides_hidden(
        self, make_temp_directory: Path, capsys: CaptureFixture[str]
    ) -> None:
        """
        Проверяет скрытие скрытых файлов без флага -all
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        """
        (make_temp_directory / ".hidden").write_text("hidden")
        (make_temp_directory / "visible.txt").write_text("visible")

        tokens = argparse.Namespace(
            paths=[str(make_temp_directory)], l=False, al=False, all=False
        )
        Ls().execute(tokens)
        captured = capsys.readouterr()

        assert ".hidden" not in captured.out
        assert "visible.txt" in captured.out

    def test_ls_al_flag_detailed_with_all(
        self, make_temp_directory: Path, capsys: CaptureFixture[str]
    ) -> None:
        """
        Проверяет комбинированный флаг -al
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        """
        (make_temp_directory / ".hidden").write_text("hidden")
        (make_temp_directory / "file.txt").write_text("content")

        tokens = argparse.Namespace(
            paths=[str(make_temp_directory)], l=False, al=True, all=False
        )
        Ls().execute(tokens)
        captured = capsys.readouterr()

        assert ".hidden" in captured.out
        assert "file.txt" in captured.out
        assert "-rw" in captured.out or "drwx" in captured.out

    def test_ls_nonexistent_directory_raises_error(
        self, make_temp_directory: Path
    ) -> None:
        """
        Проверяет ошибку при несуществующей директории
        :param make_temp_directory: Фикстура для временных директорий
        :raises ShellError: При несуществующей директории
        """
        tokens = argparse.Namespace(
            paths=[str(make_temp_directory / "nonexistent")],
            l=False,
            al=False,
            all=False,
        )
        with pytest.raises(ShellError):
            Ls().execute(tokens)

    def test_ls_file_instead_of_directory_raises_error(
        self, make_temp_directory: Path
    ) -> None:
        """
        Проверяет ошибку при попытке ls для файла
        :param make_temp_directory: Фикстура для временных директорий
        :raises ShellError: При попытке листить файл
        """
        file = make_temp_directory / "file.txt"
        file.write_text("content")

        tokens = argparse.Namespace(
            paths=[str(file)], l=False, al=False, all=False
        )
        with pytest.raises(ShellError):
            Ls().execute(tokens)

    def test_ls_sorted_output(
        self, make_temp_directory: Path, capsys: CaptureFixture[str]
    ) -> None:
        """
        Проверяет сортировку вывода
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        """
        (make_temp_directory / "z.txt").write_text("z")
        (make_temp_directory / "a.txt").write_text("a")
        (make_temp_directory / "m.txt").write_text("m")

        tokens = argparse.Namespace(
            paths=[str(make_temp_directory)], l=False, al=False, all=False
        )
        Ls().execute(tokens)
        captured = capsys.readouterr()

        output = captured.out
        a_pos = output.find("a.txt")
        m_pos = output.find("m.txt")
        z_pos = output.find("z.txt")

        assert a_pos < m_pos < z_pos

    def test_ls_multiple_directories(
        self, make_temp_directory: Path, capsys: CaptureFixture[str]
    ) -> None:
        """
        Проверяет вывод нескольких директорий
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        """
        dir1 = make_temp_directory / "dir1"
        dir2 = make_temp_directory / "dir2"
        dir1.mkdir()
        dir2.mkdir()
        (dir1 / "file1.txt").write_text("content")
        (dir2 / "file2.txt").write_text("content")

        tokens = argparse.Namespace(
            paths=[str(dir1), str(dir2)], l=False, al=False, all=False
        )
        Ls().execute(tokens)
        captured = capsys.readouterr()

        assert str(dir1) in captured.out
        assert str(dir2) in captured.out
        assert "file1.txt" in captured.out
        assert "file2.txt" in captured.out

    def test_ls_empty_directory(
        self, make_temp_directory: Path, capsys: CaptureFixture[str]
    ) -> None:
        """
        Проверяет вывод пустой директории
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        """
        empty_dir = make_temp_directory / "empty"
        empty_dir.mkdir()

        tokens = argparse.Namespace(
            paths=[str(empty_dir)], l=False, al=False, all=False
        )
        Ls().execute(tokens)
        captured = capsys.readouterr()

        assert str(empty_dir) in captured.out

    def test_ls_relative_path(
        self,
        make_temp_directory: Path,
        capsys: CaptureFixture[str],
        monkeypatch: MonkeyPatch,
    ) -> None:
        """
        Проверяет вывод по относительному пути
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        :param monkeypatch: Фикстура для изменения окружения
        """
        (make_temp_directory / "file.txt").write_text("content")
        monkeypatch.chdir(make_temp_directory)

        tokens = argparse.Namespace(paths=["."], l=False, al=False, all=False)
        Ls().execute(tokens)
        captured = capsys.readouterr()

        assert "file.txt" in captured.out

    def test_ls_absolute_path(
        self, make_temp_directory: Path, capsys: CaptureFixture[str]
    ) -> None:
        """
        Проверяет вывод по абсолютному пути
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        """
        (make_temp_directory / "file.txt").write_text("content")
        (make_temp_directory / "another.txt").write_text("another")

        absolute_path = str(make_temp_directory.resolve())

        tokens = argparse.Namespace(
            paths=[absolute_path], l=False, al=False, all=False
        )
        Ls().execute(tokens)
        captured = capsys.readouterr()

        assert "file.txt" in captured.out
        assert "another.txt" in captured.out
