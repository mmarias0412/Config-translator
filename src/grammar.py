"""Грамматика учебного конфигурационного языка.

Парсер построен на библиотеке pyparsing. Действия разбора сразу
превращают найденный текст в узлы синтаксического дерева из
модуля :mod:`src.nodes`.
"""

import pyparsing as pp

from src.errors import ConfigSyntaxError
from src.nodes import (
    Array,
    Declaration,
    Dictionary,
    Entry,
    Number,
    Program,
    Ref,
)

NAME_PATTERN = r"[a-z][a-z0-9_]*"
NUMBER_PATTERN = r"\d*\.\d+(?![\w.])"
REF_PATTERN = r"\.\{(?P<name>" + NAME_PATTERN + r")\}\.(?![\w.])"
EXPECTED_PREFIX = "Expected "
MESSAGE_TERMS = {"end of text": "конец текста"}


def _position(source, location):
    """Возвращает (строку, столбец) с единицы для позиции в тексте."""
    return pp.lineno(location, source), pp.col(location, source)


def _make_number(tokens):
    """Строит узел Number из числового литерала."""
    return Number(float(tokens[0]))


def _make_ref(source, location, tokens):
    """Строит узел Ref из вычисления константы."""
    line, column = _position(source, location)
    return Ref(tokens["name"], line, column)


def _make_array(tokens):
    """Строит узел Array из найденных значений."""
    return Array(tuple(tokens))


def _make_entry(source, location, tokens):
    """Строит узел Entry из имени и значения."""
    line, column = _position(source, location)
    name, value = tokens
    return Entry(name, value, line, column)


def _make_dictionary(tokens):
    """Строит узел Dictionary из найденных пар."""
    return Dictionary(tuple(tokens))


def _make_declaration(source, location, tokens):
    """Строит узел Declaration из имени и значения."""
    line, column = _position(source, location)
    name, value = tokens
    return Declaration(name, value, line, column)


def _make_program(tokens):
    """Строит узел Program: объявления и затем корневое значение."""
    *declarations, root = tokens
    return Program(tuple(declarations), root)


def _build_value():
    """Строит рекурсивную грамматику значения."""
    value = pp.Forward()
    number = pp.Regex(NUMBER_PATTERN).set_name("число")
    number.set_parse_action(_make_number)
    reference = pp.Regex(REF_PATTERN).set_name("ссылка на константу")
    reference.set_parse_action(_make_ref)
    array = pp.Suppress("'(") - pp.ZeroOrMore(value) + pp.Suppress(")")
    array.set_parse_action(_make_array)
    name = pp.Regex(NAME_PATTERN).set_name("имя")
    entry = name + pp.Suppress("=>") - value
    entry.set_parse_action(_make_entry)
    entries = pp.DelimitedList(entry, allow_trailing_delim=True)
    dictionary = pp.Suppress("[") - pp.Optional(entries) + pp.Suppress("]")
    dictionary.set_parse_action(_make_dictionary)
    choice = number | reference | array | dictionary
    value <<= choice.set_name("значение")
    return value


def _build_program():
    """Строит грамматику всей конфигурации."""
    value = _build_value()
    name = pp.Regex(NAME_PATTERN).set_name("имя")
    declaration = (
        pp.Suppress(pp.Keyword("let"))
        - name
        - pp.Suppress("=")
        - value
    )
    declaration.set_parse_action(_make_declaration)
    program = pp.ZeroOrMore(declaration) + value
    program.set_parse_action(_make_program)
    return program


_PROGRAM = _build_program()


def _translate_message(message):
    """Переводит сообщение pyparsing об ожидаемом на русский язык."""
    if not message.startswith(EXPECTED_PREFIX):
        return message
    expected = message[len(EXPECTED_PREFIX):]
    return f"ожидалось: {MESSAGE_TERMS.get(expected, expected)}"


def parse_text(text):
    """Разбирает текст конфигурации в узел Program.

    Аргументы:
        text: Текст на учебном конфигурационном языке.

    Возвращает:
        Синтаксическое дерево Program.

    Исключения:
        ConfigSyntaxError: Текст не соответствует грамматике.
    """
    try:
        return _PROGRAM.parse_string(text, parse_all=True)[0]
    except pp.ParseBaseException as error:
        message = _translate_message(error.msg)
        raise ConfigSyntaxError(message, error.lineno, error.col) from error
