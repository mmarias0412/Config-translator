"""Трансляция учебного конфигурационного языка в JSON."""

import json

from src.evaluator import evaluate_program
from src.grammar import parse_text

JSON_INDENT = 2


def translate(text):
    """Транслирует текст конфигурации в документ JSON.

    Аргументы:
        text: Текст на учебном конфигурационном языке.

    Возвращает:
        Текст JSON.

    Исключения:
        ConfigError: В тексте есть синтаксические ошибки или ошибки имён.
    """
    value = evaluate_program(parse_text(text))
    return json.dumps(value, indent=JSON_INDENT)
