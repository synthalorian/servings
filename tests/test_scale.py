import io
import os
import subprocess
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from servings.__main__ import main

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ScaleTests(unittest.TestCase):
    def run_scale(self, text, args):
        stdout = io.StringIO()
        stderr = io.StringIO()
        stdin = io.StringIO(text)
        with redirect_stdout(stdout), redirect_stderr(stderr), patch("sys.stdin", stdin):
            try:
                code = main(args)
            except SystemExit as exc:
                code = exc.code
        return code, stdout.getvalue(), stderr.getvalue()

    def test_flour_scales_and_converts_to_grams(self):
        code, out, err = self.run_scale("2 cups flour\n", ["scale", "--from", "4", "--to", "6"])
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        self.assertEqual(out, "3 cups flour (360 g)\n")

    def test_sugar_half_uses_cups_and_grams(self):
        code, out, err = self.run_scale("1 cup sugar\n", ["scale", "--from", "2", "--to", "1"])
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        self.assertEqual(out, "0.5 cups sugar (100 g)\n")

    def test_unknown_unit_exits_2(self):
        code, out, err = self.run_scale("1 oz flour\n", ["scale", "--from", "1", "--to", "1"])
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("line 1", err)
        self.assertIn("unknown unit", err)

    def test_bad_line_names_line_number_on_stderr(self):
        text = "2 cups flour\nnot an ingredient\n1 tsp salt\n"
        code, out, err = self.run_scale(text, ["scale", "--from", "4", "--to", "6"])
        self.assertEqual(code, 2)
        self.assertIn("line 2", err)
        self.assertNotIn("line 3", err)
        self.assertEqual(out, "3 cups flour (360 g)\n")

    def test_from_must_be_greater_than_zero(self):
        for bad in ("0", "-1", "0.0"):
            code, out, err = self.run_scale("1 cup flour\n", ["scale", "--from", bad, "--to", "1"])
            self.assertEqual(code, 2, bad)
            self.assertEqual(out, "")
            self.assertIn("--from", err)

    def test_singular_cup_when_scaled_quantity_is_one(self):
        code, out, err = self.run_scale("2 cups flour\n", ["scale", "--from", "2", "--to", "1"])
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        self.assertEqual(out, "1 cup flour (120 g)\n")

    def test_input_cup_pluralizes_when_scaled_quantity_is_not_one(self):
        code, out, err = self.run_scale("1 cup flour\n", ["scale", "--from", "1", "--to", "2"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "2 cups flour (240 g)\n")

    def test_staple_names_are_case_insensitive_and_exact(self):
        code, out, err = self.run_scale("2 cups FLOUR\n", ["scale", "--from", "4", "--to", "6"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "3 cups FLOUR (360 g)\n")

        code, out, err = self.run_scale(
            "2 cups all-purpose flour\n", ["scale", "--from", "4", "--to", "6"]
        )
        self.assertEqual(code, 0)
        self.assertEqual(out, "3 cups all-purpose flour\n")

    def test_staple_table(self):
        expected = {
            "flour": 120,
            "sugar": 200,
            "butter": 227,
            "rice": 185,
            "milk": 240,
            "water": 240,
        }
        lines = "".join(f"1 cup {name}\n" for name in expected)
        code, out, err = self.run_scale(lines, ["scale", "--from", "1", "--to", "1"])
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        rendered = "".join(f"1 cup {name} ({grams} g)\n" for name, grams in expected.items())
        self.assertEqual(out, rendered)

    def test_non_cup_units_are_kept_without_grams(self):
        text = "2 tbsp butter\n3 tsp salt\n100 g rice\n"
        code, out, err = self.run_scale(text, ["scale", "--from", "4", "--to", "2"])
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        self.assertEqual(out, "1 tbsp butter\n1.5 tsp salt\n50 g rice\n")

    def test_decimal_quantities(self):
        code, out, err = self.run_scale(".5 cups sugar\n2. tsp salt\n", ["scale", "--from", "1", "--to", "2"])
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        self.assertEqual(out, "1 cup sugar (200 g)\n4 tsp salt\n")

    def test_trailing_zeros_stripped_and_two_decimal_places(self):
        text = "1.50 tsp salt\n2.00 g salt\n1 tsp salt\n"
        code, out, err = self.run_scale(text, ["scale", "--from", "3", "--to", "1"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "0.5 tsp salt\n0.67 g salt\n0.33 tsp salt\n")

    def test_grams_round_half_up(self):
        code, out, err = self.run_scale("1 cup butter\n", ["scale", "--from", "2", "--to", "1"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "0.5 cups butter (114 g)\n")

        code, out, err = self.run_scale("15 cups flour\n", ["scale", "--from", "16", "--to", "1"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "0.94 cups flour (113 g)\n")

    def test_module_command(self):
        env = os.environ.copy()
        env["PYTHONPATH"] = ROOT + os.pathsep + env.get("PYTHONPATH", "")
        result = subprocess.run(
            [sys.executable, "-m", "servings", "scale", "--from", "4", "--to", "6"],
            input="2 cups flour\n",
            text=True,
            capture_output=True,
            cwd=ROOT,
            env=env,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "3 cups flour (360 g)\n")
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
