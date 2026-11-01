import unittest
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import update_stats as stats


class CompletedMonthTests(unittest.TestCase):
    def test_calendar_selection_does_not_depend_on_api_order(self):
        rows = [{"d": d} for d in ("2026 September", "2026 November", "2026 October")]
        self.assertEqual(stats.completed_months(rows, date(2026, 11, 1)), [rows[2], rows[0]])

    def test_current_month_need_not_be_in_response(self):
        rows = [{"d": "2026 October"}, {"d": "2026 September"}]
        self.assertEqual(stats.completed_months(rows, date(2026, 11, 30)), rows)

    def test_january_selects_previous_year(self):
        rows = [{"d": "2027 January"}, {"d": "2026 December"}]
        self.assertEqual(stats.completed_months(rows, date(2027, 1, 1)), [rows[1]])

    def test_missing_previous_month_does_not_fall_back(self):
        for rows in ([], [{"d": "2026 November"}, {"d": "2026 September"}]):
            with self.subTest(rows=rows), self.assertRaisesRegex(ValueError, "2026-10"):
                stats.completed_months(rows, date(2026, 11, 1))

    def run_update(self, today, month, days, complete):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            readme = root / "README.md"
            original = "Before\n<!-- STATS:START -->old<!-- STATS:END -->\nAfter\n"
            readme.write_text(original, encoding="utf-8")
            year, name = month.split()
            volumes = [{"d": month, "v": 1000, "o": 100, "m": 2}]
            daily = [{"d": f"{year} {d}th {name}", "p": d * 100} for d in reversed(days)]
            with (
                patch.object(stats, "ROOT", root),
                patch.object(stats, "ASSETS_DIR", root / "assets"),
                patch.object(stats, "STATS_DIR", root / "stats"),
                patch.object(stats, "datetime") as clock,
                patch.object(stats, "fetch_json", side_effect=[volumes, daily]),
                patch.object(stats, "update_featured_trade"),
                patch("builtins.print"),
            ):
                clock.now.return_value.date.return_value = today
                if complete:
                    stats.main()
                    text = readme.read_text(encoding="utf-8")
                    self.assertTrue(text.startswith("Before\n"))
                    self.assertTrue(text.endswith("\nAfter\n"))
                    slug = f"{year}-{stats.MONTH_MAP[name]:02d}"
                    month_text = (root / "stats" / f"{slug}.md").read_text(encoding="utf-8")
                    self.assertEqual(month_text.count(f"| {slug}-"), len(days))
                    self.assertIn(f"| {slug}-{max(days):02d} |", month_text)
                    chart = (root / "assets/stats-current-month.svg").read_text(encoding="utf-8")
                    self.assertEqual(chart.count("<rect "), len(days))
                else:
                    with self.assertRaisesRegex(ValueError, "incomplete"):
                        stats.main()
                    self.assertEqual(readme.read_text(encoding="utf-8"), original)
                    self.assertEqual(list((root / "stats").iterdir()), [])
                    self.assertEqual(list((root / "assets").iterdir()), [])

    def test_full_october_includes_last_day(self):
        self.run_update(date(2026, 11, 1), "2026 October", list(range(1, 32)), True)

    def test_missing_or_duplicate_day_leaves_publication_unchanged(self):
        for days in ([], list(range(1, 31)), list(range(1, 32)) + [31]):
            with self.subTest(days=days):
                self.run_update(date(2026, 11, 1), "2026 October", days, False)

    def test_february_requires_leap_day_only_in_leap_year(self):
        self.run_update(date(2024, 3, 1), "2024 February", list(range(1, 30)), True)
        self.run_update(date(2024, 3, 1), "2024 February", list(range(1, 29)), False)
        self.run_update(date(2025, 3, 1), "2025 February", list(range(1, 29)), True)


if __name__ == "__main__":
    unittest.main()
