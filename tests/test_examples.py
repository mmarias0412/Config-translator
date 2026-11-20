"""Тесты, которые транслируют примеры конфигураций."""

import json
import unittest
from pathlib import Path

from src.translator import translate

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"

SMART_HOME = {
    "thermostat": {
        "day_target": 21.5,
        "night_target": 18.0,
        "hysteresis": 0.5,
        "schedule": [6.3, 18.0, 22.0, 21.5],
    },
    "lamp": {"brightness": 0.8, "warm_levels": [0.2, 0.5, 0.8]},
}

BANK_TARIFFS = {
    "deposit": {
        "rate": 0.075,
        "bonus_rate": 0.01,
        "tiers": [10000.0, 50000.0, 100000.0],
    },
    "card": {
        "monthly_fee": 1.5,
        "cashback": [0.01, 0.02, 0.05],
        "limits": {
            "daily": 5000.0,
            "monthly": [10000.0, 50000.0, 100000.0],
        },
    },
}


def translate_example(name):
    """Транслирует файл примера и разбирает полученный JSON."""
    text = (EXAMPLES / name).read_text(encoding="utf-8")
    return json.loads(translate(text))


class ExampleTests(unittest.TestCase):
    """Примеры из разных областей транслируются как описано."""

    def test_smart_home(self):
        """Конфигурация умного дома."""
        self.assertEqual(translate_example("smart_home.conf"), SMART_HOME)

    def test_bank_tariffs(self):
        """Конфигурация банковских тарифов."""
        self.assertEqual(translate_example("bank_tariffs.conf"), BANK_TARIFFS)


if __name__ == "__main__":
    unittest.main()
