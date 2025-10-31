import logging


class Logger:
    """
    Класс для логирования
    """

    @classmethod
    def setup_logging(cls) -> None:
        """
        Настраивает логирование
        """
        logging.basicConfig(
            filename="shell.log",
            level=logging.INFO,
            format="[%(asctime)s] %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    @classmethod
    def start_execution(cls, command: str) -> None:
        """
        Логирует начало выполнения команды
        :param command: Команда для логирования
        """
        logging.info(f"STARTED: {command}")

    @classmethod
    def success_execution(cls, command: str) -> None:
        """
        Логирует успешное выполнение команды
        :param command: Команда для логирования
        """
        logging.info(f"SUCCESS: {command}")

    @classmethod
    def failure_execution(cls, message: Exception) -> None:
        """
        Логирует ошибку выполнения команды
        :param message: Сообщение об ошибке
        """
        logging.error(f"{type(message).__name__}: {message}")
