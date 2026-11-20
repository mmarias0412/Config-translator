"""Исключения транслятора учебного конфигурационного языка."""


class ConfigError(Exception):
    """Базовый класс всех ошибок транслятора.

    Атрибуты:
        message: Описание проблемы для человека.
        line: Номер строки (с единицы) или None, если он неизвестен.
        column: Номер столбца (с единицы) или None, если он неизвестен.
    """

    def __init__(self, message, line=None, column=None):
        """Запоминает сообщение и необязательную позицию ошибки."""
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column

    def __str__(self):
        """Возвращает сообщение с позицией, если она известна."""
        if self.line is None:
            return self.message
        return f"строка {self.line}, столбец {self.column}: {self.message}"


class ConfigSyntaxError(ConfigError):
    """Входной текст нарушает грамматику языка."""


class ConfigNameError(ConfigError):
    """Константа не определена или объявлена повторно, либо ключ повторён."""
