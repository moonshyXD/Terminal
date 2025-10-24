import os
import shutil

from logger import setup
from src.errors import ShellError


def main():
    setup.setup_logging()
    initial_dir = os.getcwd()
    print(f"Начальная директория: {initial_dir}")

    try:
        shutil.copy("README.txt", "pizda")

    except ShellError as e:
        print(f"Ошибка: {e}")

    os.chdir(initial_dir)
    print(f"\nВернулись в: {os.getcwd()}")


if __name__ == "__main__":
    main()
