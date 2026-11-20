"""Тесты парсера учебного конфигурационного языка."""

import unittest

from src.errors import ConfigSyntaxError
from src.grammar import parse_text
from src.nodes import Array, Declaration, Dictionary, Number, Ref


def root_of(text):
    """Разбирает текст и возвращает корневой узел."""
    return parse_text(text).root


class NumberTests(unittest.TestCase):
    """Числа соответствуют шаблону \\d*\\.\\d+."""

    def test_fraction_without_integer_part(self):
        """Число может начинаться с точки."""
        self.assertEqual(root_of(".5"), Number(0.5))

    def test_decimal(self):
        """У числа может быть целая часть."""
        self.assertEqual(root_of("12.75"), Number(12.75))

    def test_trailing_zero(self):
        """Нули в конце сохраняются как значение float."""
        self.assertEqual(root_of("3.0"), Number(3.0))

    def test_integer_is_rejected(self):
        """Число без точки является синтаксической ошибкой."""
        with self.assertRaises(ConfigSyntaxError):
            parse_text("5")

    def test_trailing_dot_is_rejected(self):
        """После точки в числе нужны цифры."""
        with self.assertRaises(ConfigSyntaxError):
            parse_text("5.")

    def test_glued_numbers_are_rejected(self):
        """Два числа должны разделяться пробельным символом."""
        with self.assertRaises(ConfigSyntaxError):
            parse_text("1.5.5")


class ArrayTests(unittest.TestCase):
    """Массивы имеют вид '( значение значение ... )."""

    def test_flat_array(self):
        """Массив хранит значения, разделённые пробелами."""
        expected = Array((Number(1.5), Number(0.2)))
        self.assertEqual(root_of("'( 1.5 .2 )"), expected)

    def test_empty_array(self):
        """Массив может быть пустым."""
        self.assertEqual(root_of("'( )"), Array(()))

    def test_nested_array(self):
        """Массивы могут быть вложенными."""
        expected = Array((Array((Number(0.1),)), Array(())))
        self.assertEqual(root_of("'( '( .1 ) '( ) )"), expected)

    def test_array_with_dictionary(self):
        """Массивы могут содержать словари."""
        node = root_of("'( [ a => .1 ] )")
        self.assertIsInstance(node.items[0], Dictionary)

    def test_commas_are_rejected(self):
        """Элементы массива разделяются пробелами, а не запятыми."""
        with self.assertRaises(ConfigSyntaxError):
            parse_text("'( .1, .2 )")

    def test_unclosed_array(self):
        """Нет закрывающей скобки: синтаксическая ошибка."""
        with self.assertRaises(ConfigSyntaxError):
            parse_text("'( .1 .2")


class DictionaryTests(unittest.TestCase):
    """Словари имеют вид [ имя => значение, ... ]."""

    def test_entries(self):
        """Пары разделяются запятыми."""
        node = root_of("[ a => .1, b_2 => .2 ]")
        self.assertEqual([e.name for e in node.entries], ["a", "b_2"])

    def test_empty_dictionary(self):
        """Словарь может быть пустым."""
        self.assertEqual(root_of("[ ]"), Dictionary(()))

    def test_trailing_comma(self):
        """Запятая после последней пары допустима."""
        node = root_of("[ a => .1, ]")
        self.assertEqual(len(node.entries), 1)

    def test_nested_dictionary(self):
        """Словари могут быть вложенными."""
        node = root_of("[ a => [ b => '( .1 ) ] ]")
        inner = node.entries[0].value
        self.assertIsInstance(inner.entries[0].value, Array)

    def test_uppercase_name_is_rejected(self):
        """Имена состоят из строчных букв, цифр и подчёркиваний."""
        with self.assertRaises(ConfigSyntaxError):
            parse_text("[ A => .1 ]")

    def test_name_starting_with_digit_is_rejected(self):
        """Имя не может начинаться с цифры."""
        with self.assertRaises(ConfigSyntaxError):
            parse_text("[ 1a => .1 ]")

    def test_wrong_arrow_is_rejected(self):
        """Имя и значение разделяет только =>."""
        with self.assertRaises(ConfigSyntaxError):
            parse_text("[ a = .1 ]")

    def test_missing_comma_is_rejected(self):
        """Пары обязаны разделяться запятыми."""
        with self.assertRaises(ConfigSyntaxError):
            parse_text("[ a => .1 b => .2 ]")

    def test_unclosed_dictionary(self):
        """Нет закрывающей скобки: синтаксическая ошибка."""
        with self.assertRaises(ConfigSyntaxError):
            parse_text("[ a => .1")


class ConstantTests(unittest.TestCase):
    """Объявления используют let, вычисления используют .{имя}."""

    def test_declaration(self):
        """Объявление разбирается до корневого значения."""
        program = parse_text("let pi = 3.14 .{pi}.")
        self.assertEqual(len(program.declarations), 1)
        self.assertIsInstance(program.declarations[0], Declaration)
        self.assertEqual(program.declarations[0].name, "pi")

    def test_evaluation_node(self):
        """Вычисление разбирается в узел Ref."""
        self.assertEqual(root_of(".{pi}."), Ref("pi", 1, 1))

    def test_evaluation_inside_containers(self):
        """Вычисления могут быть в массивах и словарях."""
        node = root_of("[ a => '( .{x}. ) ]")
        self.assertIsInstance(node.entries[0].value.items[0], Ref)

    def test_declaration_value_may_be_container(self):
        """Константа может хранить массив или словарь."""
        program = parse_text("let a = '( .1 ) let b = [ k => .2 ] .{b}.")
        self.assertEqual(len(program.declarations), 2)

    def test_keyword_prefix_is_a_name(self):
        """Имя может начинаться с ключевого слова."""
        program = parse_text("let letter = .5 .{letter}.")
        self.assertEqual(program.declarations[0].name, "letter")

    def test_declaration_without_value(self):
        """Объявлению нужно значение."""
        with self.assertRaises(ConfigSyntaxError):
            parse_text("let a = ")

    def test_declaration_with_wrong_sign(self):
        """Объявлению нужен знак =."""
        with self.assertRaises(ConfigSyntaxError):
            parse_text("let a .5 .{a}.")

    def test_evaluation_with_spaces_is_rejected(self):
        """Внутри .{имя}. пробелы недопустимы."""
        with self.assertRaises(ConfigSyntaxError):
            parse_text(".{ a }.")

    def test_evaluation_without_closing_dot(self):
        """Закрывающая точка обязательна."""
        with self.assertRaises(ConfigSyntaxError):
            parse_text(".{a}")


class ProgramTests(unittest.TestCase):
    """Свойства текста конфигурации целиком."""

    def test_empty_text(self):
        """В пустом тексте нет корневого значения."""
        with self.assertRaises(ConfigSyntaxError):
            parse_text("")

    def test_only_declarations(self):
        """Объявления без корневого значения отклоняются."""
        with self.assertRaises(ConfigSyntaxError):
            parse_text("let a = .5")

    def test_garbage_after_root(self):
        """Лишний текст после корневого значения отклоняется."""
        with self.assertRaises(ConfigSyntaxError):
            parse_text(".5 .5")

    def test_error_position(self):
        """Ошибки сообщают строку и столбец."""
        with self.assertRaises(ConfigSyntaxError) as context:
            parse_text("let a = .5\n[ a => ]")
        self.assertEqual(context.exception.line, 2)
        self.assertEqual(context.exception.column, 8)

    def test_error_message_text(self):
        """Сообщение об ошибке содержит позицию."""
        with self.assertRaises(ConfigSyntaxError) as context:
            parse_text("x")
        message = str(context.exception)
        self.assertTrue(message.startswith("строка 1, столбец 1"))


if __name__ == "__main__":
    unittest.main()
