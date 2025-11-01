from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch


@pytest.fixture
def temp_path(tmp_path: Path) -> Path:
    """
    Алиас для tmp_path
    :param tmp_path: Фикстура для временных директорий
    :return: Объект временной директории
    """
    return tmp_path


@pytest.fixture
def make_temp_directory(temp_path: Path) -> Path:
    """
    Создаёт временную директорию для тестов
    :param temp_path: Фикстура для временных директорий
    :return: Объект временной директории
    """
    return temp_path


@pytest.fixture
def make_temp_file(temp_path: Path) -> Path:
    """
    Создаёт временный тестовый файл с содержимым
    :param temp_path: Фикстура для временных директорий
    :return: Объект файла temp.txt
    """
    file = temp_path / "temp.txt"
    file.write_text("Temp")
    return file


@pytest.fixture
def make_temp_structure(temp_path: Path) -> Path:
    """
    Создаёт временную тестовую директорию с файлами и вложенной структурой
    :param temp_path: Фикстура для временных директорий
    :return: Объект директории с тестовыми файлами
    """
    dir_path = temp_path / "temp_directory"
    dir_path.mkdir()
    (dir_path / "file1.txt").write_text("file1")
    (dir_path / "file2.txt").write_text("file2")
    (dir_path / "subdirectory").mkdir()
    (dir_path / "subdirectory" / "nested.txt").write_text("nested content")
    return dir_path


@pytest.fixture(autouse=True)
def change_to_history_directory(
    temp_path: Path, monkeypatch: MonkeyPatch
) -> Path:
    """
    Меняет рабочую директорию на временную и создаёт структуру history
    :param temp_path: Фикстура для временных директорий
    :param monkeypatch: Фикстура для мокирования
    :return: Объект временной директории
    """
    history_dir = temp_path / "src" / "history"
    history_dir.mkdir(parents=True, exist_ok=True)
    (history_dir / ".history").touch()
    (history_dir / ".undo_history").touch()
    (history_dir / ".trash").mkdir(exist_ok=True)

    monkeypatch.chdir(temp_path)
    return temp_path


@pytest.fixture(autouse=True)
def disable_logging():
    """
    Отключает логгирование для тестов
    """
    import logging

    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)
