"""Интерфейс командной строки транслятора конфигураций."""

import argparse
import sys
from pathlib import Path

from src.errors import ConfigError
from src.translator import translate

EXIT_OK = 0
EXIT_ERROR = 1
INPUT_ENCODING = "utf-8-sig"


def build_arg_parser():
    """Создаёт разборщик аргументов командной строки."""
    parser = argparse.ArgumentParser(
        prog="config-translator",
        description=(
            "Транслирует конфигурацию на учебном языке в JSON "
            "и печатает его в стандартный вывод."
        ),
    )
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        metavar="FILE",
        help="путь к файлу с текстом конфигурации",
    )
    return parser


def run(argv=None):
    """Запускает транслятор и возвращает код завершения процесса.

    Аргументы:
        argv: Аргументы командной строки; при None берётся sys.argv.

    Возвращает:
        EXIT_OK при успехе и EXIT_ERROR при любой выведенной ошибке.
    """
    args = build_arg_parser().parse_args(argv)
    try:
        text = Path(args.input).read_text(encoding=INPUT_ENCODING)
    except (OSError, UnicodeDecodeError) as error:
        message = f"ошибка: не удалось прочитать '{args.input}': {error}"
        print(message, file=sys.stderr)
        return EXIT_ERROR
    try:
        print(translate(text))
    except ConfigError as error:
        print(f"ошибка: {error}", file=sys.stderr)
        return EXIT_ERROR
    return EXIT_OK
