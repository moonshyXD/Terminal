import argparse
import os
import re

from src.errors import ShellError
from src.file_commands.base_command import BaseClass


class Grep(BaseClass):
    def execute(self, tokens: argparse.Namespace):
        try:
            regex = re.compile("".join(tokens.pattern[0]))
            interactive = tokens.interactive
            recursive = tokens.recursive
            paths = tokens.paths if tokens.paths else [os.getcwd()]

            self._grep_paths(paths, regex, recursive, interactive)
        except Exception as message:
            raise ShellError(str(message)) from None

    def _grep_paths(
        self, paths: list, regex, recursive: bool, interactive: bool
    ):
        for path in paths:
            abs_path = self._abs_path(path)
            self._path_exists(abs_path)

            if os.path.isfile(abs_path):
                self._find_coincidence(abs_path, regex, interactive)
            elif os.path.isdir(abs_path):
                if recursive:
                    for item in os.listdir(abs_path):
                        item_path = os.path.join(abs_path, item)
                        self._grep_paths(
                            [item_path], regex, recursive, interactive
                        )
                else:
                    for item in os.listdir(abs_path):
                        item_path = os.path.join(abs_path, item)
                        if os.path.isfile(item_path):
                            self._find_coincidence(
                                item_path, regex, interactive
                            )

    def _find_coincidence(self, file_path: str, regex, interactive: bool):
        line_number = 1
        with open(file_path, "r") as file:
            for line in file:
                if interactive:
                    line = line.lower()

                if regex.search(line):
                    print(f"{file_path}:{line_number}:{line.rstrip()}")

                line_number += 1
