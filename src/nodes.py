"""Типы узлов синтаксического дерева, которые строит парсер."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Number:
    """Числовой литерал, например ``.5`` или ``3.14``."""

    value: float


@dataclass(frozen=True)
class Ref:
    """Вычисление константы на этапе трансляции ``.{имя}.``."""

    name: str
    line: int
    column: int


@dataclass(frozen=True)
class Array:
    """Массив ``'( значение значение ... )``."""

    items: tuple


@dataclass(frozen=True)
class Entry:
    """Одна пара ``имя => значение`` словаря."""

    name: str
    value: object
    line: int
    column: int


@dataclass(frozen=True)
class Dictionary:
    """Словарь ``[ имя => значение, ... ]``."""

    entries: tuple


@dataclass(frozen=True)
class Declaration:
    """Объявление константы ``let имя = значение``."""

    name: str
    value: object
    line: int
    column: int


@dataclass(frozen=True)
class Program:
    """Вся конфигурация: объявления констант и корневое значение."""

    declarations: tuple
    root: object
