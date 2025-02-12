import unittest
from datetime import timedelta

from config.parser import parse_timedelta_value, parse_timedelta_interval


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


    def test_mixed_value_1(self):
        result = parse_timedelta_value("1d3h4m2s1ms")
        self.assertEqual(
            timedelta(days=1,hours=3,minutes=4,seconds=2,milliseconds=1),
            result
        )


    def test_negative_values_1(self):
        result = parse_timedelta_value("-1d3h4m2s1ms")
        self.assertEqual(
            -timedelta(days=1,hours=3,minutes=4,seconds=2,milliseconds=1),
            result
        )


    def test_negative_values_2_spaces(self):
        result = parse_timedelta_value(" - 50s")
        self.assertEqual(
            -timedelta(seconds=50),
            result
        )


    def test_negative_values_invalid(self):
        with self.assertRaises(ValueError):
            parse_timedelta_value("3d -4s")


    def test_mixed_value_2(self):
        result = parse_timedelta_value("3h13s99ms")
        self.assertEqual(
            timedelta(hours=3,seconds=13,milliseconds=99),
            result
        )


    def test_mixed_value_wrong_order(self):
        with self.assertRaises(ValueError):
            parse_timedelta_value("3h4d")


    def test_invalid_value(self):
        with self.assertRaises(ValueError):
            parse_timedelta_value("1235443gg")


class TimeDeltaRangeTests(unittest.TestCase):

    def test_empty_value(self):
        result = parse_timedelta_interval("")
        self.assertEqual(timedelta(), result)


    def test_one_value(self):
        result = parse_timedelta_interval("1h13s")
        self.assertEqual(
            timedelta(hours=1,seconds=13),
            result
        )


    def test_two_values(self):
        result = parse_timedelta_interval("390ms~3m")
        self.assertEqual(
            {
                "from": timedelta(milliseconds=390),
                "to": timedelta(minutes=3)
            },
            result
        )


    def test_one_value_with_spaces(self):
        result = parse_timedelta_interval(" 1h13s    ")
        self.assertEqual(
            timedelta(hours=1,seconds=13),
            result
        )


    def test_two_values_with_spaces(self):
        result = parse_timedelta_interval(" 390ms ~ 3m ")
        self.assertEqual(
            {
                "from": timedelta(milliseconds=390),
                "to": timedelta(minutes=3)
            },
            result
        )


    def test_single_negative_value(self):
        result = parse_timedelta_interval("-2d45m")
        self.assertEqual(-timedelta(days=2,minutes=45),result)


    def test_negative_values_1(self):
        result = parse_timedelta_interval(" -1d3h4m2s1ms ~ -2d45m")
        self.assertEqual(
            {
                "from": -timedelta(days=1,hours=3,minutes=4,seconds=2,milliseconds=1),
                "to": -timedelta(days=2,minutes=45),
            },
            result
        )


    def test_negative_values_2(self):
        result = parse_timedelta_interval(" -50s ~ -1m")
        self.assertEqual(
            {
                "from": -timedelta(seconds=50),
                "to": -timedelta(minutes=1),
            },
            result
        )


    def test_negative_values_invalid(self):
        with self.assertRaises(ValueError):
            parse_timedelta_interval("3d -4s ~ 5d")


    def test_invalid_value(self):
        with self.assertRaises(ValueError):
            parse_timedelta_interval("121ddf")


    def test_invalid_values(self):
        with self.assertRaises(ValueError):
            parse_timedelta_interval("121ddf~1275hjf")


if __name__ == '__main__':
    unittest.main()
