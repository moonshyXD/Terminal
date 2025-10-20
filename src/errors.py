class ShellError(Exception):
    """Базовая ошибка"""

    pass


class PathNotFoundError(ShellError):
    """Путь не найден"""

    pass


class NotAFileError(ShellError):
    """Объект не является файлом"""

    pass


class NotADirectoryError(ShellError):
    """Объект не является директорией"""

    pass
