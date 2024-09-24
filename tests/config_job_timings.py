import unittest
from datetime import timedelta, datetime

from config.parser import configure_job_timings


class JobTimingsTests(unittest.TestCase):

    def test_empty_value(self):
        with self.assertRaises(KeyError):
            configure_job_timings({})


    def test_no_frequency(self):
        config = {
            "startTime": "2024-10-9 10:00",
            "endTime": "2024-10-9 15:00",
        }
        with self.assertRaises(KeyError):
            configure_job_timings(config)


    def test_no_offset_with_same_start_end_1(self):
        config = {
            "frequency": "30s"
        }
        with self.assertRaises(ValueError):
            configure_job_timings(config)


    def test_no_offset_with_same_start_end_2(self):
        config = {
            "frequency": "30s",
            "startTime": "2024-10-9 15:00",
            "endTime": "2024-10-9 15:00"
        }
        with self.assertRaises(ValueError):
            configure_job_timings(config)


    def test_same_start_end_with_offset(self):
        config = {
            "frequency": "3.5m",
            "endOffset": "7h"
        }
        configure_job_timings(config)
        self.assertFalse(config["live"])
        self.assertEqual(timedelta(minutes=3.5), config["frequency"])
        self.assertEqual(config["startTime"], config["originalEndTime"])
        self.assertEqual(config["originalEndTime"] + timedelta(hours=7), config["endTime"])
        self.assertEqual(config["endOffset"], timedelta(hours=7))
        self.assertNotIn("startOffset", config)


    def test_defaults_1(self):
        config: dict[str, any] = {
            "frequency": "30s",
            "startTime": "2024-10-09 15:00",
            "endOffset": "5m"
        }
        configure_job_timings(config)
        self.assertFalse(config["live"])
        self.assertEqual(timedelta(seconds=30), config["frequency"])
        self.assertEqual(config["startTime"], config["originalEndTime"])
        self.assertEqual(config["startTime"] + timedelta(minutes=5), config["endTime"])
        self.assertEqual(config["endOffset"], timedelta(minutes=5))
        self.assertIn("endTime", config)
        self.assertNotIn("startOffset", config)


    def test_defaults_2(self):
        config: dict[str, any] = {
            "frequency": "13m",
            "endTime": "2024-10-09 15:00",
            "startOffset": "-90s"
        }
        configure_job_timings(config)
        self.assertFalse(config["live"])
        self.assertEqual(timedelta(minutes=13), config["frequency"])
        self.assertEqual(config["endTime"], config["originalStartTime"])
        self.assertEqual(config["endTime"] - timedelta(seconds=90), config["startTime"])
        self.assertEqual(config["startOffset"], timedelta(seconds=-90))
        self.assertIn("startTime", config)
        self.assertNotIn("endOffset", config)


    def test_defaults_3(self):
        config = {
            "frequency": "1h~2h",
            "startTime": "2024-10-09 15:00",
            "endTime": "2024-10-12 15:00",
            "startOffset": "10s~99s"
        }
        configure_job_timings(config)
        self.assertFalse(config["live"])
        self.assertEqual({
            "from": timedelta(hours=1),
            "to": timedelta(hours=2)
        }, config["frequency"])
        self.assertEqual(config["originalStartTime"], datetime.fromisoformat("2024-10-09 15:00"))
        self.assertEqual(config["endTime"], datetime.fromisoformat("2024-10-12 15:00"))
        self.assertEqual(config["startOffset"], {
            "from": timedelta(seconds=10),
            "to": timedelta(seconds=99)
        })
        self.assertIn("startTime", config)
        self.assertNotIn("endOffset", config)


if __name__ == '__main__':
    unittest.main()
