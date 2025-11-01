import argparse
from pathlib import Path

from _pytest.capture import CaptureFixture
from _pytest.monkeypatch import MonkeyPatch

from src.history.history import History


class TestsHistory:
    """Тесты для History"""

    def test_history_init(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет инициализацию History
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        monkeypatch.chdir(make_temp_directory)

        history = History()

        assert history.history_path is not None
        assert "src/history/.history" in history.history_path

    def test_execute_displays_history(
        self,
        make_temp_directory: Path,
        capsys: CaptureFixture[str],
        monkeypatch: MonkeyPatch,
    ) -> None:
        """
        Проверяет вывод истории
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        :param monkeypatch: Фикстура для изменения окружения
        """
        history_file = make_temp_directory / "src" / "history" / ".history"
        history_file.write_text("1 ls\n2 cd /home\n3 cat file.txt\n")

        monkeypatch.chdir(make_temp_directory)
        history = History()

        tokens = argparse.Namespace(count=2)
        history.execute(tokens)
        captured = capsys.readouterr()

        assert "2 cd /home" in captured.out
        assert "3 cat file.txt" in captured.out

    def test_execute_with_count_1(
        self,
        make_temp_directory: Path,
        capsys: CaptureFixture[str],
        monkeypatch: MonkeyPatch,
    ) -> None:
        """
        Проверяет вывод одной команды
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        :param monkeypatch: Фикстура для изменения окружения
        """
        history_file = make_temp_directory / "src" / "history" / ".history"
        history_file.write_text("1 ls\n2 cd /home\n3 cat file.txt\n")

        monkeypatch.chdir(make_temp_directory)
        history = History()

        tokens = argparse.Namespace(count=1)
        history.execute(tokens)
        captured = capsys.readouterr()

        assert "3 cat file.txt" in captured.out

    def test_get_line_number_returns_string(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет возврат номера строки как строки
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        history_file = make_temp_directory / "src" / "history" / ".history"
        history_file.write_text("1 ls\n2 cd /home\n3 cat file.txt\n")

        monkeypatch.chdir(make_temp_directory)
        history = History()

        line_number = history._get_line_number()

        assert line_number == "3"

    def test_get_line_number_extracts_number(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет что извлекается только номер
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        history_file = make_temp_directory / "src" / "history" / ".history"
        history_file.write_text("1 ls\n5 grep pattern directory\n")

        monkeypatch.chdir(make_temp_directory)
        history = History()

        line_number = history._get_line_number()

        assert line_number == "5"
        assert isinstance(line_number, str)

    def test_add_history_appends_to_file(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет что команда добавляется в конец файла
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        history_file = make_temp_directory / "src" / "history" / ".history"
        history_file.write_text("1 ls\n")

        monkeypatch.chdir(make_temp_directory)
        history = History()

        history.add_history("cd /home\n")
        history.add_history("mkdir test\n")

        lines = history_file.read_text().strip().split("\n")
        assert len(lines) == 3
        assert lines[-1].startswith("3")

    def test_add_history_correct_format(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет формат записи в историю
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        history_file = make_temp_directory / "src" / "history" / ".history"
        history_file.write_text("1 ls\n")

        monkeypatch.chdir(make_temp_directory)
        history = History()

        history.add_history("grep pattern file.txt\n")

        content = history_file.read_text()
        assert "2 grep pattern file.txt" in content

    def test_execute_empty_history(
        self,
        make_temp_directory: Path,
        capsys: CaptureFixture[str],
        monkeypatch: MonkeyPatch,
    ) -> None:
        """
        Проверяет вывод пустой истории
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        :param monkeypatch: Фикстура для изменения окружения
        """
        history_file = make_temp_directory / "src" / "history" / ".history"
        history_file.write_text("")

        monkeypatch.chdir(make_temp_directory)
        history = History()

        tokens = argparse.Namespace(count=5)
        history.execute(tokens)
        captured = capsys.readouterr()

        assert captured.out == ""

    def test_execute_large_count(
        self,
        make_temp_directory: Path,
        capsys: CaptureFixture[str],
        monkeypatch: MonkeyPatch,
    ) -> None:
        """
        Проверяет вывод с количеством больше чем команд в истории
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        :param monkeypatch: Фикстура для изменения окружения
        """
        history_file = make_temp_directory / "src" / "history" / ".history"
        history_file.write_text("1 ls\n2 cd /home\n")

        monkeypatch.chdir(make_temp_directory)
        history = History()

        tokens = argparse.Namespace(count=100)
        history.execute(tokens)
        captured = capsys.readouterr()

        assert "1 ls" in captured.out
        assert "2 cd /home" in captured.out

    def test_get_history_with_multiword_commands(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет _get_history с многословными командами
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        history_file = make_temp_directory / "src" / "history" / ".history"
        history_file.write_text(
            "1 grep -r 'pattern' /home\n2 cp -r src dest\n"
        )

        monkeypatch.chdir(make_temp_directory)
        history = History()

        result = history._get_history(2)

        assert len(result) == 2
        assert "grep -r 'pattern' /home" in list(result)[0]

    def test_add_history_multiple_times(
        self, make_temp_directory: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        Проверяет добавление нескольких команд подряд
        :param make_temp_directory: Фикстура для временных директорий
        :param monkeypatch: Фикстура для изменения окружения
        """
        history_file = make_temp_directory / "src" / "history" / ".history"
        history_file.write_text("1 ls\n")

        monkeypatch.chdir(make_temp_directory)
        history = History()

        for i in range(5):
            history.add_history(f"command{i}\n")

        content = history_file.read_text()
        lines = content.strip().split("\n")

        assert len(lines) == 6
        assert lines[-1].startswith("6")

    def test_execute_preserves_formatting(
        self,
        make_temp_directory: Path,
        capsys: CaptureFixture[str],
        monkeypatch: MonkeyPatch,
    ) -> None:
        """
        Проверяет что форматирование истории сохраняется
        :param make_temp_directory: Фикстура для временных директорий
        :param capsys: Фикстура для захвата stdout
        :param monkeypatch: Фикстура для изменения окружения
        """
        history_file = make_temp_directory / "src" / "history" / ".history"
        history_file.write_text("1 ls\n2 cd /home\n3 mkdir test\n")

        monkeypatch.chdir(make_temp_directory)
        history = History()

        tokens = argparse.Namespace(count=3)
        history.execute(tokens)
        captured = capsys.readouterr()

        assert captured.out.count("\n") >= 3
