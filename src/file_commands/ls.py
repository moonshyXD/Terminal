import argparse
import os
import stat
from datetime import datetime

from src.errors import ShellError
from src.file_commands.base_command import BaseClass


class Ls(BaseClass):
    def execute(self, tokens: argparse.Namespace) -> None:
        try:
            if tokens.paths:
                paths = tokens.paths
            else:
                paths = [os.getcwd()]

            detailed = tokens.l

            for path in paths:
                abs_path = self._abs_path(path)

                self._path_exists(abs_path)
                self._is_directory(abs_path)

                items = os.listdir(abs_path)

                print(f"{path}:")
                if detailed:
                    self._print_detailed(items, abs_path)
                else:
                    self._print_not_detailed(items)

                print()
        except Exception as message:
            raise ShellError(str(message)) from None

    def _print_detailed(self, items: list, abs_path: str) -> None:
        for item in sorted(items):
            item_path = os.path.join(abs_path, item)

            stats = os.stat(item_path)

            mode = stat.filemode(stats.st_mode)

            item_size = stats.st_size

            mtime = datetime.fromtimestamp(stats.st_mtime)
            mtime_str = mtime.strftime("%Y-%m-%d %H:%M")

            log = f"{mode} {item_size:>10} {mtime_str} {item}"
            if item[0] != ".":
                print(log)

    def _print_not_detailed(self, items: list) -> None:
        for item in sorted(items):
            if item[0] != ".":
                print(f"{item}", end=" ")
        print()
