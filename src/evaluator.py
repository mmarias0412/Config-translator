"""Вычисление констант на этапе трансляции и преобразование дерева."""

from src.errors import ConfigNameError
from src.nodes import Array, Dictionary, Number, Ref


def evaluate_program(program):
    """Вычисляет узел Program в обычные значения Python.

    Константы объявляются по порядку, поэтому константа может
    ссылаться только на объявленные выше.

    Аргументы:
        program: Синтаксическое дерево от парсера.

    Возвращает:
        Значение корня: float, list или dict.

    Исключения:
        ConfigNameError: Константа не определена или объявлена
            повторно, либо в словаре повторяется ключ.
    """
    constants = {}
    for declaration in program.declarations:
        _declare(declaration, constants)
    return _evaluate(program.root, constants)


def _declare(declaration, constants):
    """Вычисляет объявление и сохраняет константу."""
    if declaration.name in constants:
        raise ConfigNameError(
            f"константа '{declaration.name}' уже объявлена",
            declaration.line,
            declaration.column,
        )
    constants[declaration.name] = _evaluate(declaration.value, constants)


def _evaluate(node, constants):
    """Преобразует узел значения в значение Python."""
    if isinstance(node, Number):
        return node.value
    if isinstance(node, Ref):
        return _lookup(node, constants)
    if isinstance(node, Array):
        return [_evaluate(item, constants) for item in node.items]
    if isinstance(node, Dictionary):
        return _evaluate_dictionary(node, constants)
    raise TypeError(f"неподдерживаемый узел: {node!r}")


def _lookup(reference, constants):
    """Возвращает значение константы, на которую ссылается узел Ref."""
    if reference.name not in constants:
        raise ConfigNameError(
            f"константа '{reference.name}' не определена",
            reference.line,
            reference.column,
        )
    return constants[reference.name]


def _evaluate_dictionary(dictionary, constants):
    """Преобразует узел Dictionary в dict, отклоняя повторные ключи."""
    result = {}
    for entry in dictionary.entries:
        if entry.name in result:
            raise ConfigNameError(
                f"повторяющийся ключ '{entry.name}'", entry.line, entry.column
            )
        result[entry.name] = _evaluate(entry.value, constants)
    return result
