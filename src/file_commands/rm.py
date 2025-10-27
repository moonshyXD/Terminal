import argparse
import os
import shutil

from src.errors import DeletingError, ShellError
from src.file_commands.base_command import BaseClass


class Rm(BaseClass):
    def __init__(self):
        self._command = self.__class__.__name__.lower()
        self.trash_path = os.path.join(os.getcwd(), "src/history/.trash")
        self.undo_history_path = os.path.join(
            os.getcwd(), "src/history/.undo_history"
        )

    def execute(self, tokens: argparse.Namespace):
        try:
            if not tokens.paths:
                paths = [os.path.expanduser("~")]
            else:
                paths = tokens.paths

            directory = tokens.recursive

            for path in paths:
                abs_path = self._abs_path(path)
                self._path_exists(abs_path)

                if directory:
                    self._is_directory(abs_path)
                    self._is_root(abs_path)
                    print(f"Are you sure that you wanna delete {path}? [y/n]")
                    accept = input()
                    if accept == "y":
                        filename = os.path.basename(abs_path)
                        shutil.move(
                            abs_path, os.path.join(self.trash_path, filename)
                        )

                        self._save_undo_info(filename, os.getcwd())
                    else:
                        print(f"Cancel deleting {path}...")
                        continue
                else:
                    self._is_file(abs_path)
                    filename = os.path.basename(abs_path)
                    shutil.move(
                        abs_path, os.path.join(self.trash_path, filename)
                    )

                    self._save_undo_info(filename, os.getcwd())

        except Exception as message:
            raise ShellError(str(message)) from None

    def _save_undo_info(self, filename: str, original_dir: str):
        undo_line = f"rm {filename} {original_dir}\n"

        with open(self.undo_history_path, "a", encoding="utf-8") as file:
            file.write(undo_line)

    def _is_root(self, path: str):
        root_paths = [
            "/",
            "/root",
            "/home",
            "/usr",
            "/etc",
            "/var",
            "/sys",
            "/proc",
            "C:\\",
            "C:\\Windows",
            "C:\\Program Files",
        ]
        if (
            path in root_paths
            or path == os.path.expanduser("~")
            or path == os.getcwd()
            or path == os.path.dirname(os.getcwd())
        ):
            raise DeletingError("Cannot delete root directory")

        ancestor = os.path.normpath(path)
        target = os.path.normpath(os.getcwd())

        if not ancestor.endswith(os.sep):
            ancestor += os.sep

        if target.startswith(ancestor):
            raise DeletingError("Cannot delete parent directory")
