"""Тесты интерфейса командной строки."""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from src.cli import EXIT_ERROR, EXIT_OK, run


class CliTests(unittest.TestCase):
    """Утилита читает файл и печатает JSON в стандартный вывод."""

    def setUp(self):
        """Создаёт временный каталог для входных файлов."""
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)

    def write(self, text, encoding="utf-8"):
        """Записывает входной файл и возвращает его путь."""
        path = Path(self.directory.name) / "input.conf"
        path.write_text(text, encoding=encoding)
        return str(path)

    def call(self, argv):
        """Запускает утилиту и возвращает (код, stdout, stderr)."""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out):
            with contextlib.redirect_stderr(err):
                code = run(argv)
        return code, out.getvalue(), err.getvalue()

    def test_success(self):
        """Корректный файл транслируется в JSON."""
        path = self.write("let x = .5 [ a => .{x}. ]")
        code, out, err = self.call(["--input", path])
        self.assertEqual(code, EXIT_OK)
        self.assertEqual(json.loads(out), {"a": 0.5})
        self.assertEqual(err, "")

    def test_short_key(self):
        """Короткий ключ -i работает как --input."""
        path = self.write("'( .1 )")
        code, out, _ = self.call(["-i", path])
        self.assertEqual(code, EXIT_OK)
        self.assertEqual(json.loads(out), [0.1])

    def test_bom_is_accepted(self):
        """Файл, сохранённый с BOM, читается корректно."""
        path = self.write(".5", encoding="utf-8-sig")
        code, out, _ = self.call(["-i", path])
        self.assertEqual(code, EXIT_OK)
        self.assertEqual(json.loads(out), 0.5)

    def test_syntax_error(self):
        """Синтаксическая ошибка выводится в стандартный поток ошибок."""
        path = self.write("[ a => ")
        code, out, err = self.call(["-i", path])
        self.assertEqual(code, EXIT_ERROR)
        self.assertEqual(out, "")
        self.assertIn("строка 1", err)

    def test_name_error(self):
        """Ошибка имени выводится в стандартный поток ошибок."""
        path = self.write("[ a => .{q}. ]")
        code, _, err = self.call(["-i", path])
        self.assertEqual(code, EXIT_ERROR)
        self.assertIn("'q' не определена", err)

    def test_missing_file(self):
        """Отсутствие входного файла выводится в поток ошибок."""
        code, _, err = self.call(["-i", "missing-file.conf"])
        self.assertEqual(code, EXIT_ERROR)
        self.assertIn("не удалось прочитать", err)

    def test_missing_key(self):
        """Ключ --input обязателен."""
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                run([])


if __name__ == "__main__":
    unittest.main()
