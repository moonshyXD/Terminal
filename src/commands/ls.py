import os
import stat
from datetime import datetime

from commands.base_command import BaseClass
from errors import ShellError


class Ls(BaseClass):
    def execute(self, path: str, detailed: bool) -> None:
        try:
            abs_path = self._abs_path(path)

            self._path_exists(abs_path)
            self._is_directory(abs_path)
            self._is_execution(abs_path)

            items = os.listdir(abs_path)

            if detailed:
                self._print_detalied(items, abs_path)
            else:
                self._print_not_detailed(items)

            self._success_execution(abs_path)
        except Exception as message:
            self._failure_execution(path, str(message))
            raise ShellError(str(message)) from None

    def _print_detalied(self, items: list, abs_path: str) -> None:
        for item in sorted(items):
            item_path = os.path.join(abs_path, item)

            stats = os.stat(item_path)
            mode = stat.filemode(stats.st_mode)
            item_size = stats.st_size

            mtime = datetime.fromtimestamp(stats.st_mtime)
            mtime_str = mtime.strftime("%Y-%m-%d %H:%M")

            log = f"{mode} {item_size:>10} {mtime_str} {item}"
            print(log)

    def _print_not_detailed(self, items: list) -> None:
        sorted_items = sorted(items)
        print(" ".join(sorted_items))
