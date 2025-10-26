import argparse
import os
import shutil

from src.errors import DeletingError, ShellError
from src.file_commands.base_command import BaseClass


class Rm(BaseClass):
    def __init__(self):
        self.trash_path = os.path.join(os.getcwd(), "src/history/.trash")

    def execute(self, tokens: argparse.Namespace):
        if not tokens.paths:
            paths = [os.path.expanduser("~")]
        else:
            paths = tokens.paths

        directory = tokens.r or tokens.recursive
        try:
            abs_path = self._abs_path(paths[0])

            self._start_execution(paths)
            self._path_exists(abs_path)

            if directory:
                self._is_directory(abs_path)
                self._is_root(abs_path)
                print("Are you sure that you wanna delete this? [y/n]")
                accept = input()
                if accept == "y":
                    shutil.move(abs_path, self.trash_path)
                else:
                    print("Cancel deleting...")

            else:
                self._is_file(abs_path)
                shutil.move(abs_path, self.trash_path)

            tokens.paths += [os.getcwd()]

        except Exception as message:
            self._failure_execution(paths, str(message))
            raise ShellError(str(message)) from None

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
