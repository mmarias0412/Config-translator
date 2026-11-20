"""Тесты вычисления констант и трансляции в JSON."""

import json
import unittest

from src.errors import ConfigNameError, ConfigSyntaxError
from src.evaluator import evaluate_program
from src.grammar import parse_text
from src.translator import translate


def evaluate(text):
    """Разбирает и вычисляет текст."""
    return evaluate_program(parse_text(text))


class ValueTests(unittest.TestCase):
    """Преобразование литералов и контейнеров."""

    def test_number(self):
        """Число становится float."""
        self.assertEqual(evaluate(".25"), 0.25)

    def test_array(self):
        """Массив становится списком."""
        self.assertEqual(evaluate("'( .1 2.5 )"), [0.1, 2.5])

    def test_dictionary(self):
        """Словарь становится dict с сохранением порядка ключей."""
        result = evaluate("[ b => .1, a => .2 ]")
        self.assertEqual(list(result.items()), [("b", 0.1), ("a", 0.2)])

    def test_nested(self):
        """Вложенные контейнеры преобразуются рекурсивно."""
        result = evaluate("[ a => '( [ b => .5 ] '( ) ) ]")
        self.assertEqual(result, {"a": [{"b": 0.5}, []]})


class ConstantTests(unittest.TestCase):
    """Константы вычисляются на этапе трансляции."""

    def test_number_constant(self):
        """Числовая константа подставляется."""
        self.assertEqual(evaluate("let x = .5 .{x}."), 0.5)

    def test_constant_in_array(self):
        """Константу можно использовать внутри массива."""
        self.assertEqual(evaluate("let x = .5 '( .{x}. .{x}. )"), [0.5, 0.5])

    def test_constant_in_dictionary(self):
        """Константу можно использовать как значение словаря."""
        self.assertEqual(evaluate("let x = .5 [ k => .{x}. ]"), {"k": 0.5})

    def test_container_constant(self):
        """Константа может хранить целый словарь."""
        text = "let d = [ a => .1 ] '( .{d}. .{d}. )"
        self.assertEqual(evaluate(text), [{"a": 0.1}, {"a": 0.1}])

    def test_constant_from_constant(self):
        """Константа может использовать ранее объявленную."""
        text = "let a = .5 let b = '( .{a}. ) .{b}."
        self.assertEqual(evaluate(text), [0.5])

    def test_nested_evaluation(self):
        """Вычисление работает на любой глубине вложенности."""
        text = "let a = .5 [ x => [ y => '( [ z => .{a}. ] ) ] ]"
        expected = {"x": {"y": [{"z": 0.5}]}}
        self.assertEqual(evaluate(text), expected)

    def test_undefined_constant(self):
        """Неизвестная константа даёт ошибку имени с позицией."""
        with self.assertRaises(ConfigNameError) as context:
            evaluate("[ a => .{zz}. ]")
        self.assertEqual(context.exception.column, 8)
        self.assertIn("'zz'", str(context.exception))

    def test_use_before_declaration(self):
        """Константу нельзя использовать до её объявления."""
        with self.assertRaises(ConfigNameError):
            evaluate("let a = .{b}. let b = .5 .{a}.")

    def test_redefinition(self):
        """Константу нельзя объявить дважды."""
        with self.assertRaises(ConfigNameError):
            evaluate("let a = .5 let a = .6 .{a}.")

    def test_duplicate_key(self):
        """В словаре не может быть повторяющихся ключей."""
        with self.assertRaises(ConfigNameError):
            evaluate("[ a => .1, a => .2 ]")


class TranslateTests(unittest.TestCase):
    """Трансляция текста в JSON."""

    def test_json_output(self):
        """Результат является корректным документом JSON."""
        text = "let x = .5 [ a => '( .{x}. 1.0 ) ]"
        self.assertEqual(json.loads(translate(text)), {"a": [0.5, 1.0]})

    def test_float_is_kept(self):
        """Целое значение сохраняет дробную часть в JSON."""
        self.assertEqual(translate("3.0"), "3.0")

    def test_syntax_error_is_propagated(self):
        """Синтаксические ошибки пробрасываются из translate."""
        with self.assertRaises(ConfigSyntaxError):
            translate("[ a => ")


if __name__ == "__main__":
    unittest.main()
