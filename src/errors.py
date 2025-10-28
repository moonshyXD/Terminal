class ShellError(Exception):
    """Базовая ошибка"""

    pass


class PathNotFoundError(ShellError):
    """Путь не найден"""

    pass


class NotAFileError(ShellError):
    """Не является файлом"""

    pass


class NotADirectoryError(ShellError):
    """Не является директорией"""

    pass


class NotTextFileError(ShellError):
    """Не является текстовым файлом"""

    pass


class CommandNotFoundError(ShellError):
    """Команда для отмены не найдена"""

    pass


class ParserError(ShellError):
    """Ошибка парсинга аргументов"""

    pass


class DeletingError(ShellError):
    """Ошибка при удалении"""

    pass


class MovingError(ShellError):
    """Ошибка при перемещении"""

    pass


class UndoError(ShellError):
    """Ошибка отмены операции"""

    pass


class InvalidPathError(ShellError):
    """Недопустимый путь"""

    pass


class InvalidFileError(ShellError):
    """Недопустимый файл"""

    pass


class AlreadyExistsError(ShellError):
    """Этот файл или директория уже созданы"""

    pass
