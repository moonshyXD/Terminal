class ShellError(Exception):
    """Базовая ошибка"""

    pass


class PathNotFoundError(ShellError):
    """Путь не найден"""

    pass


class NotAFileError(ShellError):
    """Объект по пути не файл"""

    pass


class NotADirectoryError(ShellError):
    """Объект по пути не папка"""

    pass


class NotTextFile(ShellError):
    """Объект по пути не текстовый"""

    pass


class ParserError(Exception):
    pass


class DeletingError(ShellError):
    pass


class MovingError(ShellError):
    pass
