import unittest

from config.executor import expand_variables, format_str_payload


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


    def test_index_value_list(self):
        dataSources = {
            "logMessages": {
                "type": "list",
                "value": [
                    ["a1", "a2", "a3"],
                    ["b1", "b2", "b3"],
                    ["c1", "c2", "c3"],
                ]
            }
        }
        variables = [
            {
                "name": "row1",
                "dataSource": "logMessages",
                "selector": "first",
                "index": 1
            },
            {
                "name": "row3",
                "dataSource": "logMessages",
                "selector": "last",
                "index": 2
            }
        ]
        result = expand_variables(variables, dataSources)
        self.assertEqual("a2", result["row1"])
        self.assertEqual("c3", result["row3"])


    def test_index_value_dict(self):
        dataSources = {
            "logMessages": {
                "type": "list",
                "value": [
                    {"v1": "a1", "v2": "a2", "v3": "a3"},
                    {"v1": "b1", "v2": "b2", "v3": "b3"},
                    {"v1": "c1", "v2": "c2", "v3": "c3"},
                ]
            }
        }
        variables = [
            {
                "name": "v21",
                "dataSource": "logMessages",
                "selector": "first",
                "index": "v2"
            },
            {
                "name": "v32",
                "dataSource": "logMessages",
                "selector": "last",
                "index": "v3"
            }
        ]
        result = expand_variables(variables, dataSources)
        self.assertEqual("a2", result["v21"])
        self.assertEqual("c3", result["v32"])


    def test_indexed_var_dict(self):
        dataSources = {
            "logMessages": {
                "type": "fixed",
                "value": {"v1": "a1", "v2": "a2", "v3": "a3"}
            }
        }
        variables = [ "logMessages" ]
        vars_dict = expand_variables(variables, dataSources)
        result = format_str_payload(vars_dict, "Value {logMessages[v1]}")
        self.assertEqual("Value a1", result)


    def test_indexed_var_list(self):
        dataSources = {
            "logMessages": {
                "type": "fixed",
                "value": ["a1", "a2", "a3"]
            }
        }
        variables = [ "logMessages" ]
        vars_dict = expand_variables(variables, dataSources)
        result = format_str_payload(vars_dict, "Value {logMessages[2]}")
        self.assertEqual("Value a3", result)


if __name__ == '__main__':
    unittest.main()
