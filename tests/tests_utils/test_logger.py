import logging
from unittest.mock import patch

from src.utils.errors import ShellError
from src.utils.logger import Logger


class TestsLogger:
    """Тесты для Logger с 100% покрытием"""

    def test_setup_logging_creates_config(self) -> None:
        """
        Проверяет настройку логирования
        """
        with patch("logging.basicConfig") as mock_basic_config:
            Logger.setup_logging()

            mock_basic_config.assert_called_once()
            call_kwargs = mock_basic_config.call_args[1]

            assert call_kwargs["filename"] == "shell.log"
            assert call_kwargs["level"] == logging.INFO
            assert "[%(asctime)s]" in call_kwargs["format"]
            assert "%(levelname)s" in call_kwargs["format"]
            assert "%(message)s" in call_kwargs["format"]

    def test_setup_logging_format_string(self) -> None:
        """
        Проверяет формат логирования
        """
        with patch("logging.basicConfig") as mock_basic_config:
            Logger.setup_logging()

            call_kwargs = mock_basic_config.call_args[1]
            assert call_kwargs["datefmt"] == "%Y-%m-%d %H:%M:%S"

    def test_start_execution_logs_command(self) -> None:
        """
        Проверяет логирование начала выполнения команды
        """
        with patch("logging.info") as mock_info:
            Logger.start_execution("ls")

            mock_info.assert_called_once_with("STARTED: ls")

    def test_start_execution_with_different_command(self) -> None:
        """
        Проверяет логирование с разными командами
        """
        with patch("logging.info") as mock_info:
            Logger.start_execution("cat file.txt")

            mock_info.assert_called_once_with("STARTED: cat file.txt")

    def test_success_execution_logs_command(self) -> None:
        """
        Проверяет логирование успешного выполнения (покрывает logging.info)
        """
        with patch("logging.info") as mock_info:
            Logger.success_execution("cd /home")

            mock_info.assert_called_once_with("SUCCESS: cd /home")

    def test_success_execution_with_complex_command(self) -> None:
        """
        Проверяет логирование с комплексной командой
        """
        with patch("logging.info") as mock_info:
            Logger.success_execution("grep -r 'pattern' /path")

            mock_info.assert_called_once_with(
                "SUCCESS: grep -r 'pattern' /path"
            )

    def test_failure_execution_logs_exception(self) -> None:
        """
        Проверяет логирование ошибки
        """
        with patch("logging.error") as mock_error:
            error = ShellError("Test error message")
            Logger.failure_execution(error)

            mock_error.assert_called_once_with(
                "ShellError: Test error message"
            )

    def test_failure_execution_with_different_exception(self) -> None:
        """
        Проверяет логирование разных типов исключений
        """
        with patch("logging.error") as mock_error:
            error = ValueError("Invalid value")
            Logger.failure_execution(error)

            mock_error.assert_called_once_with("ValueError: Invalid value")

    def test_failure_execution_exception_name_in_message(self) -> None:
        """
        Проверяет что название исключения включено в сообщение
        """
        with patch("logging.error") as mock_error:
            error = TypeError("Type mismatch")
            Logger.failure_execution(error)

            call_args = mock_error.call_args[0][0]
            assert "TypeError" in call_args
            assert "Type mismatch" in call_args

    def test_start_execution_empty_command(self) -> None:
        """
        Проверяет логирование пустой команды
        """
        with patch("logging.info") as mock_info:
            Logger.start_execution("")

            mock_info.assert_called_once_with("STARTED: ")

    def test_success_execution_empty_command(self) -> None:
        """
        Проверяет логирование успеха пустой команды
        """
        with patch("logging.info") as mock_info:
            Logger.success_execution("")

            mock_info.assert_called_once_with("SUCCESS: ")

    def test_failure_execution_with_custom_exception(self) -> None:
        """
        Проверяет логирование кастомного исключения
        """

        class CustomError(Exception):
            pass

        with patch("logging.error") as mock_error:
            error = CustomError("Custom error")
            Logger.failure_execution(error)

            mock_error.assert_called_once_with("CustomError: Custom error")

    def test_logger_is_classmethod(self) -> None:
        """
        Проверяет что методы - это classmethods
        """
        assert isinstance(Logger.__dict__["setup_logging"], classmethod)
        assert isinstance(Logger.__dict__["start_execution"], classmethod)
        assert isinstance(Logger.__dict__["success_execution"], classmethod)
        assert isinstance(Logger.__dict__["failure_execution"], classmethod)

    def test_multiple_logging_calls(self) -> None:
        """
        Проверяет несколько вызовов логирования подряд
        """
        with patch("logging.info") as mock_info:
            Logger.start_execution("cmd1")
            Logger.success_execution("cmd1")
            Logger.start_execution("cmd2")

            assert mock_info.call_count == 3

    def test_failure_execution_exception_message_formatting(self) -> None:
        """
        Проверяет правильное форматирование сообщения об ошибке
        """
        with patch("logging.error") as mock_error:
            error = RuntimeError("Runtime problem occurred")
            Logger.failure_execution(error)

            expected = "RuntimeError: Runtime problem occurred"
            mock_error.assert_called_once_with(expected)

    def test_setup_logging_log_filename(self) -> None:
        """
        Проверяет что используется правильное имя файла логов
        """
        with patch("logging.basicConfig") as mock_basic_config:
            Logger.setup_logging()

            call_kwargs = mock_basic_config.call_args[1]
            assert call_kwargs["filename"] == "shell.log"

    def test_setup_logging_log_level(self) -> None:
        """
        Проверяет что уровень логирования - INFO
        """
        with patch("logging.basicConfig") as mock_basic_config:
            Logger.setup_logging()

            call_kwargs = mock_basic_config.call_args[1]
            assert call_kwargs["level"] == logging.INFO
