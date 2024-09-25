import unittest

from config.executor import expand_variables


class VariableExpandTests(unittest.TestCase):

    def test_extractor_value(self):
        dataSources = {
            "vmZone": {
                "type": "fixed",
                "value": "projects/228638176398/zones/europe-west3-a"
            }
        }
        variables = [
            {
                "name": "vmZone",
                "extractor": r"\/zones\/([a-z0-9\-]+)$"
            }
        ]
        result = expand_variables(variables, dataSources)
        self.assertEqual("europe-west3-a", result["vmZone"])


if __name__ == '__main__':
    unittest.main()
