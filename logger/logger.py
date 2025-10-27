import logging


class Logger():
    def setup_logging(self):
        logging.basicConfig(
            filename="logger/shell.log",
            level=logging.INFO,
            format="[%(asctime)s] %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def start_execution(self, command: str) -> None:
        logging.info(f"STARTED: {command}")

    def success_execution(self, command: str) -> None:
        logging.info(f"SUCCESS: {command}")

    def failure_execution(self, message: str) -> None:
        logging.error(message)
