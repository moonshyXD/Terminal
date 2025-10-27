import logging


class Logger:
    """
    Класс для логирования
    """
    def setup_logging(self) -> None:
        """
        Настраивает логирование
        """
        logging.basicConfig(
            filename="logger/shell.log",
            level=logging.INFO,
            format="[%(asctime)s] %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def start_execution(self, command: str) -> None:
        """
        Логирует начало выполнения команды
        :param command: Команда для логирования
        """
        logging.info(f"STARTED: {command}")

    def success_execution(self, command: str) -> None:
        """
        Логирует успешное выполнение команды
        :param command: Команда для логирования
        """
        logging.info(f"SUCCESS: {command}")

    def failure_execution(self, message: str) -> None:
        """
        Логирует ошибку выполнения команды
        :param message: Сообщение об ошибке
        """
        logging.error(message)
