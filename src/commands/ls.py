import argparse
import os
import stat
from datetime import datetime

from src.commands.base_command import BaseClass
from src.errors import ShellError


class Ls(BaseClass):
    def execute(self, tokens: argparse.Namespace) -> None:
        if tokens.paths:
            paths = tokens.paths
        else:
            paths = [os.getcwd()]

        detailed = tokens.l

        try:
            abs_path = self._abs_path(paths[0])

            log_args = ["-l"] + paths if detailed else paths
            self._start_execution(log_args)
            self._path_exists(abs_path)
            self._is_directory(abs_path)

            items = os.listdir(abs_path)

            if detailed:
                self._print_detailed(items, abs_path)
            else:
                self._print_not_detailed(items)
        except Exception as message:
            self._failure_execution(paths, str(message))
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
