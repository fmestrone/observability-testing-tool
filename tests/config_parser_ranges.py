import unittest

from config.parser import parse_float_range, parse_int_range


class FloatRangeTests(unittest.TestCase):

    def test_empty_value(self):
        with self.assertRaises(ValueError):
            parse_float_range("")


    def test_single_int_value(self):
        result = parse_float_range("13")
        self.assertEqual({ "from": 0.0, "to": 13.0 }, result)


    def test_double_int_values(self):
        result = parse_float_range("13~39")
        self.assertEqual({ "from": 13.0, "to": 39.0 }, result)


    def test_single_float_value(self):
        result = parse_float_range("13.5")
        self.assertEqual({ "from": 0.0, "to": 13.5 }, result)


    def test_double_float_values(self):
        result = parse_float_range("13.513~39.7979")
        self.assertEqual({ "from": 13.513, "to": 39.7979 }, result)


    def test_single_float_value_spaces(self):
        result = parse_float_range("  13.5 ")
        self.assertEqual({ "from": 0.0, "to": 13.5 }, result)


    def test_double_float_values_spaces(self):
        result = parse_float_range(" 13.513  ~  39.7979 ")
        self.assertEqual({ "from": 13.513, "to": 39.7979 }, result)


    def test_double_mixed_values(self):
        result = parse_float_range("13~39.379")
        self.assertEqual({ "from": 13.0, "to": 39.379 }, result)


    def test_double_negative_values(self):
        result = parse_float_range("-13~-39.379")
        self.assertEqual({ "from": -13.0, "to": -39.379 }, result)


    def test_single_nan_value(self):
        with self.assertRaises(ValueError):
            parse_float_range("aws")


    def test_double_nan_values(self):
        with self.assertRaises(ValueError):
            parse_float_range("qwe~yuj")


class IntRangeTests(unittest.TestCase):

    def test_empty_value(self):
        with self.assertRaises(ValueError):
            parse_int_range("")


    def test_single_int_value(self):
        result = parse_int_range("13")
        self.assertEqual({ "from": 0, "to": 13 }, result)


    def test_double_int_values(self):
        result = parse_int_range("13~39")
        self.assertEqual({ "from": 13, "to": 39 }, result)


    def test_single_float_value(self):
        with self.assertRaises(ValueError):
            parse_int_range("13.531")


    def test_double_float_values(self):
        with self.assertRaises(ValueError):
            parse_int_range("13.513~39.7979")


    def test_single_int_value_spaces(self):
        result = parse_int_range("  13 ")
        self.assertEqual({ "from": 0, "to": 13 }, result)


    def test_double_int_values_spaces(self):
        result = parse_int_range(" 13  ~  39 ")
        self.assertEqual({ "from": 13, "to": 39 }, result)


    def test_double_mixed_values(self):
        with self.assertRaises(ValueError):
            parse_int_range("13~39.379")


    def test_single_nan_value(self):
        with self.assertRaises(ValueError):
            parse_int_range("aws")


    def test_double_nan_values(self):
        with self.assertRaises(ValueError):
            parse_int_range("qwe~yuj")


if __name__ == '__main__':
    unittest.main()
