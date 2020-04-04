import json
from typing import Dict, Any, Optional, List, cast

import attr
from json_tcg.data import AttrClass, AttrAttribute, SchemaRepresentation

NR = 0


def next_nr() -> int:
    global NR
    NR += 1
    return NR


@attr.s()
class TypeResult:
    python_type_name = attr.ib(type=str)
    created_types = attr.ib(factory=list, type=List[AttrClass])


@attr.s()
class ObjectResult:
    attr_class = attr.ib(type=AttrClass)
    created_types = attr.ib(factory=list, type=List[AttrClass])

    def to_type_result(self) -> TypeResult:
        return TypeResult(self.attr_class.name, [self.attr_class] + self.created_types)

    def to_schema_representation(self) -> SchemaRepresentation:
        return SchemaRepresentation(self.attr_class, self.created_types)


def loads(schema_text: str) -> SchemaRepresentation:
    schema = json.loads(schema_text)
    return handle_root(schema).to_schema_representation()


def handle_root(schema_dict: Dict[str, Any]) -> ObjectResult:
    assert schema_dict['type'] == 'object'
    return create_object(schema_dict)


def create_object(schema_dict: Dict[str, Any]) -> ObjectResult:
    attributes = []
    additional_classes = []
    required_property_names = schema_dict.get('required', [])
    class_name = cast(str, schema_dict.get('title')) if 'title' in schema_dict else 'DataClass{}'.format(next_nr())
    for property_name, property_dict in schema_dict['properties'].items():
        result = get_type(property_dict)
        property_type = result.python_type_name
        property_default = None
        if property_name not in required_property_names:
            property_type = 'Optional[{}]'.format(property_type)
            property_default = 'None'
        attributes.append(AttrAttribute(property_name, property_type, property_default))
        additional_classes += result.created_types
    attributes = sorted(attributes, key=lambda a: a.has_default)
    attr_class = AttrClass(class_name, attributes)
    return ObjectResult(attr_class, additional_classes)


def get_type(schema_dict: Dict[str, Any]) -> TypeResult:
    type_name = schema_dict['type']
    if type_name == 'string':
        return TypeResult('str')
    elif type_name == 'integer':
        return TypeResult('int')
    elif type_name == 'number':
        return TypeResult('float')
    elif type_name == 'object':
        object_result = create_object(schema_dict)
        return object_result.to_type_result()
    elif type_name == 'array':
        item_type = get_type(schema_dict['items'])
        return TypeResult('List[{}]'.format(item_type.python_type_name), item_type.created_types)
    else:
        raise ValueError('Cant handle {}'.format(type_name))
