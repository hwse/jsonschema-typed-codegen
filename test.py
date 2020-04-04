
from json_tcg.schema import loads
from json_tcg.generator import dump_schema

with open('examples/person.schema.json') as f:
    object_result = loads(f.read())

print(dump_schema(object_result))