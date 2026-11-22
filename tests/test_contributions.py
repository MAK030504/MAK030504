import unittest
from datetime import date

from scripts.fetch_contributions import parse_calendar, streak_stats

SAMPLE = """
<h2>3 contributions in the last year</h2>
<td class="ContributionCalendar-day" data-date="2026-01-01" data-level="0" id="d0"></td>
<tool-tip for="d0">No contributions on January 1st.</tool-tip>
<td class="ContributionCalendar-day" data-date="2026-01-02" data-level="2" id="d1"></td>
<tool-tip for="d1">2 contributions on January 2nd.</tool-tip>
<td class="ContributionCalendar-day" data-date="2026-01-03" data-level="4" id="d2"></td>
<tool-tip for="d2">5 contributions on January 3rd.</tool-tip>
<td class="ContributionCalendar-day" data-date="2026-01-04" data-level="0" id="d3"></td>
<tool-tip for="d3">No contributions on January 4th.</tool-tip>
"""


class CalendarTests(unittest.TestCase):
    def test_parse_counts(self):
        days = parse_calendar(SAMPLE)
        self.assertEqual([item["count"] for item in days], [0, 2, 5, 0])
        self.assertEqual(days[2]["level"], 4)

    def test_streak_skips_empty_today(self):
        days = parse_calendar(SAMPLE)
        stats = streak_stats(days, today=date(2026, 1, 4))
        self.assertEqual(stats["total"], 7)
        self.assertEqual(stats["longest_streak"], 2)
        self.assertEqual(stats["current_streak"], 2)
        self.assertEqual(stats["best_count"], 5)


if __name__ == "__main__":
    unittest.main()
