import unittest

from json_tcg.schema import handle_root
from json_tcg.generator import dump_attr_class

SCHEMA = {
    "type": "object",
    "properties": {
        "name": {
            "description": "Formatted Name",
            "type": "string"
        },
        "salary": {
            "type": "integer"
        },
        "address": {
            "type": "object",
            "properties": {
                "street": {
                    "type": "string"
                },
                "nr": {
                    "type": "integer"
                }
            }
        }
    }
}


class TestSchemaParse(unittest.TestCase):

    def test_handle_root(self):
        result = handle_root(SCHEMA)


