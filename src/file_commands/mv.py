import argparse
import logging
import os
import re
import shutil

from src.errors import MovingError, PathNotFoundError, ShellError
from src.file_commands.base_command import BaseClass


class Mv(BaseClass):
    def __init__(self):
        self._command = self.__class__.__name__.lower()
        self.undo_history_path = os.path.join(
            os.getcwd(), "src/history/.undo_history"
        )

    def execute(self, tokens: argparse.Namespace):
        try:
            self._is_tokens(tokens)

            paths = tokens.paths

            abs_to_path = self._abs_path(paths[len(paths) - 1])

            for path in paths:
                abs_from_path = self._abs_path(path)

                self._path_exists(abs_from_path)

                if not os.access(abs_from_path, os.R_OK):
                    message = (
                        f"Невозможно получить доступ '{paths[0]}': "
                        f"Нет прав доступа"
                    )
                    logging.error(message)
                    raise MovingError(message)

                target_dir = os.path.dirname(abs_to_path) or "."
                if not os.access(target_dir, os.W_OK):
                    message = (
                        f"Невозможно переместить '{paths[1]}': "
                        f"Нет прав доступа"
                    )
                    logging.error(message)
                    raise MovingError(message)

                shutil.move(abs_from_path, abs_to_path)

            self._optimize_paths_for_undo(tokens)
        except Exception as message:
            raise ShellError(str(message)) from None

    def _optimize_paths_for_undo(self, tokens: argparse.Namespace):
        for path in tokens.paths[:-1]:
            match = re.search(r"([^/]+)/?$", path)
            if match:
                moved_element = match.group(1)

                destination = os.path.join(os.getcwd(), tokens.paths[-1])
                final_path = os.path.join(destination, moved_element)

                original_dir = os.getcwd()

                undo_line = f"mv {final_path} {original_dir}\n"

                with open(
                    self.undo_history_path, "a", encoding="utf-8"
                ) as file:
                    file.write(undo_line)

    def _is_tokens(self, tokens: argparse.Namespace):
        if not tokens.paths or len(tokens.paths) < 2:
            message = "Отсутствует путь файла"
            logging.error(message)
            raise PathNotFoundError(message) from None
