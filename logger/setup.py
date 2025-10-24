import logging


def setup_logging():
    logging.basicConfig(
        filename="logger/shell.log",
        level=logging.INFO,
        format="[%(asctime)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
