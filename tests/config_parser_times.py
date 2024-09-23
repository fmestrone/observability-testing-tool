import unittest
from datetime import timedelta

from config.parser import parse_timedelta_value


class TimeDeltaTests(unittest.TestCase):

    def test_empty_value(self):
        result = parse_timedelta_value("")
        self.assertEqual(timedelta(), result)


    def test_seconds_value(self):
        result = parse_timedelta_value("13s")
        self.assertEqual(timedelta(seconds=13), result)


    def test_milliseconds_value(self):
        result = parse_timedelta_value("390ms")
        self.assertEqual(timedelta(milliseconds=390), result)


    def test_minutes_value(self):
        result = parse_timedelta_value("15m")
        self.assertEqual(timedelta(minutes=15), result)


    def test_hours_value(self):
        result = parse_timedelta_value("3h")
        self.assertEqual(timedelta(hours=3), result)


    def test_days_value(self):
        result = parse_timedelta_value("7d")
        self.assertEqual(timedelta(days=7), result)


if __name__ == '__main__':
    unittest.main()
