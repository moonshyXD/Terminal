import argparse
import os
from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch

from src.filesystem.base_command import BaseClass
from src.utils.errors import (
    InvalidPathError,
    NotADirectoryError,
    NotAFileError,
    PathNotFoundError,
)


class ConcreteCommand(BaseClass):
    """Класс для тестов BaseClass"""

    def execute(self, tokens: argparse.Namespace) -> None:
        pass


class TestsBaseCommand:
    """Тесты для BaseClass"""

    def test_abs_path_with_tilde(self) -> None:
        """
        Проверяет преобразование ~ в домашнюю директорию
        """
        cmd = ConcreteCommand()
        home = os.path.expanduser("~")

        result = cmd._abs_path("~")

        assert result == home

    def test_abs_path_with_parent_dir(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет преобразование .. в родительскую директорию
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        subdir = make_temp_directory / "subdir"
        subdir.mkdir()
        monkeypatch.chdir(subdir)

        cmd = ConcreteCommand()
        result = cmd._abs_path("..")

        assert result == str(make_temp_directory)

    def test_abs_path_relative_path(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет преобразование относительного пути в абсолютный
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        monkeypatch.chdir(make_temp_directory)
        cmd = ConcreteCommand()

        result = cmd._abs_path("file.txt")

        assert result == str(make_temp_directory / "file.txt")

    def test_abs_path_absolute_path(self, make_temp_directory: Path) -> None:
        """
        Проверяет возврат абсолютного пути как есть
        :param make_temp_directory: Фикстура для временных директорий
        """
        cmd = ConcreteCommand()
        abs_path = str(make_temp_directory)

        result = cmd._abs_path(abs_path)

        assert result == abs_path

    def test_correct_path_valid_path(self, make_temp_directory: Path) -> None:
        """
        Проверяет валидный путь
        :param make_temp_directory: Фикстура для временных директорий
        """
        cmd = ConcreteCommand()

        cmd._correct_path(str(make_temp_directory / "file.txt"))

    def test_correct_path_with_hash(self) -> None:
        """
        Проверяет ошибку при # в пути
        :raises InvalidPathError: При наличии # в пути
        """
        cmd = ConcreteCommand()

        with pytest.raises(InvalidPathError) as exc_info:
            cmd._correct_path("file#name.txt")
        assert "#" in str(exc_info.value)

    def test_correct_path_with_ampersand(self) -> None:
        """
        Проверяет ошибку при & в пути
        :raises InvalidPathError: При наличии & в пути
        """
        cmd = ConcreteCommand()

        with pytest.raises(InvalidPathError) as exc_info:
            cmd._correct_path("file&name.txt")
        assert "&" in str(exc_info.value)

    def test_correct_path_with_parenthesis(self) -> None:
        """
        Проверяет ошибку при ( в пути
        :raises InvalidPathError: При наличии ( в пути
        """
        cmd = ConcreteCommand()

        with pytest.raises(InvalidPathError) as exc_info:
            cmd._correct_path("file(name).txt")
        assert "(" in str(exc_info.value)

    def test_correct_path_with_asterisk(self) -> None:
        """
        Проверяет ошибку при * в пути
        :raises InvalidPathError: При наличии * в пути
        """
        cmd = ConcreteCommand()

        with pytest.raises(InvalidPathError) as exc_info:
            cmd._correct_path("file*name.txt")
        assert "*" in str(exc_info.value)

    def test_correct_path_with_question_mark(self) -> None:
        """
        Проверяет ошибку при ? в пути
        :raises InvalidPathError: При наличии ? в пути
        """
        cmd = ConcreteCommand()

        with pytest.raises(InvalidPathError) as exc_info:
            cmd._correct_path("file?name.txt")
        assert "?" in str(exc_info.value)

    def test_correct_path_with_pipe(self) -> None:
        """
        Проверяет ошибку при | в пути
        :raises InvalidPathError: При наличии | в пути
        """
        cmd = ConcreteCommand()

        with pytest.raises(InvalidPathError) as exc_info:
            cmd._correct_path("file|name.txt")
        assert "|" in str(exc_info.value)

    def test_correct_path_with_angle_brackets(self) -> None:
        """
        Проверяет ошибку при < или > в пути
        :raises InvalidPathError: При наличии < в пути
        """
        cmd = ConcreteCommand()

        with pytest.raises(InvalidPathError) as exc_info:
            cmd._correct_path("file<name.txt")
        assert "<" in str(exc_info.value)

        with pytest.raises(InvalidPathError) as exc_info:
            cmd._correct_path("file>name.txt")
        assert ">" in str(exc_info.value)

    def test_correct_path_with_backtick(self) -> None:
        """
        Проверяет ошибку при ` в пути
        :raises InvalidPathError: При наличии ` в пути
        """
        cmd = ConcreteCommand()

        with pytest.raises(InvalidPathError) as exc_info:
            cmd._correct_path("file`name.txt")
        assert "`" in str(exc_info.value)

    def test_path_exists_valid_path(self, make_temp_directory: Path) -> None:
        """
        Проверяет существующий путь
        :param make_temp_directory: Фикстура для временных директорий
        """
        cmd = ConcreteCommand()

        cmd._path_exists(str(make_temp_directory))

    def test_path_exists_nonexistent_path(
        self, make_temp_directory: Path
    ) -> None:
        """
        Проверяет несуществующий путь
        :param make_temp_directory: Фикстура для временных директорий
        :raises PathNotFoundError: При несуществующем пути
        """
        cmd = ConcreteCommand()

        with pytest.raises(PathNotFoundError) as exc_info:
            cmd._path_exists(str(make_temp_directory / "nonexistent"))
        assert "не найдены" in str(exc_info.value)

    def test_is_file_not_file_directory(
        self, make_temp_directory: Path
    ) -> None:
        """
        Проверяет ошибку когда это директория
        :param make_temp_directory: Фикстура для временных директорий
        :raises NotAFileError: Когда путь - директория
        """
        cmd = ConcreteCommand()

        with pytest.raises(NotAFileError) as exc_info:
            cmd._is_file(str(make_temp_directory))
        assert "Не является файлом" in str(exc_info.value)

    def test_is_directory_not_directory_file(
        self, make_temp_directory: Path
    ) -> None:
        """
        Проверяет ошибку когда это файл
        :param make_temp_directory: Фикстура для временных директорий
        :raises NotADirectoryError: Когда путь - файл
        """
        file = make_temp_directory / "file.txt"
        file.write_text("content")
        cmd = ConcreteCommand()

        with pytest.raises(NotADirectoryError) as exc_info:
            cmd._is_directory(str(file))
        assert "Не является директорией" in str(exc_info.value)

    def test_is_tokens_with_valid_paths(self) -> None:
        """
        Проверяет валидные пути в tokens
        """
        cmd = ConcreteCommand()
        tokens = argparse.Namespace(paths=["/path/to/file"])

        cmd._is_tokens(tokens)

    def test_is_tokens_empty_paths_raises_error(self) -> None:
        """
        Проверяет ошибку при пустых путях
        :raises PathNotFoundError: При пустых путях
        """
        cmd = ConcreteCommand()
        tokens = argparse.Namespace(paths=[])

        with pytest.raises(PathNotFoundError) as exc_info:
            cmd._is_tokens(tokens)
        assert "Отсутствует путь файла" in str(exc_info.value)

    def test_is_tokens_no_paths_attribute_raises_error(self) -> None:
        """
        Проверяет ошибку при отсутствии атрибута paths
        :raises PathNotFoundError: При отсутствии paths
        """
        cmd = ConcreteCommand()
        tokens = argparse.Namespace()

        with pytest.raises(AttributeError):
            cmd._is_tokens(tokens)
