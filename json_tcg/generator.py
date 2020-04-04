import re
from typing import List, TypeVar, Iterable

from json_tcg.data import AttrClass, AttrAttribute, SchemaRepresentation

ONE_EMPTY_LINE = ['']


def indent(line: str, spaces: int = 4) -> str:
    return " " * spaces + line


T = TypeVar('T')


def flatten(nested_iterable: Iterable[Iterable[T]]) -> List[T]:
    return [item for sub_iterable in nested_iterable for item in sub_iterable]


def enquote(text: str, quote_char: str = '\'') -> str:
    return quote_char + text + quote_char


SNAKE_PATTERN = re.compile(r'(?<!^)(?=[A-Z])')


def to_snake_case(text: str) -> str:
    return SNAKE_PATTERN.sub('_', text).lower()


def dump_attr_attribute(attr_attribute: AttrAttribute) -> str:
    attrib_parameters = ['type={}'.format(attr_attribute.type)]
    if attr_attribute.default is not None:
        attrib_parameters.append('default={}'.format(attr_attribute.default))
    return "{} = attr.ib({})".format(attr_attribute.name, ",".join(attrib_parameters))


def constructor_parameter(attribute: AttrAttribute) -> str:
    if attribute.has_default:
        value_template = 'dictionary[{name}] if {name} in dictionary else {default}'
    else:
        value_template = 'dictionary[{name}]'
    value = value_template.format(
        name=enquote(attribute.name),
        default=attribute.default
    )
    return '{} = {},'.format(attribute.name, value)


def dump_load_method(attr_class: AttrClass) -> List[str]:
    header = [
        '@classmethod',
        'def load(cls, dictionary: Dict[str, Any]) -> {}:'.format(enquote(attr_class.name))
    ]
    body = [
        'return cls(',
        *(indent(constructor_parameter(a)) for a in attr_class.attributes),
        ')'
    ]
    return [
        *header,
        *(indent(line) for line in body)
    ]


def dump_dump_method(attr_class: AttrClass) -> List[str]:
    header = [
        'def dump(self) -> Dict[str, Any]:'
    ]
    required_attributes = (a for a in attr_class.attributes if not a.has_default)
    result_creation = [
        'result = {',
        *(indent('\'{name}\': self.{name}'.format(name=a.name)) for a in required_attributes),
        '}'
    ]
    optional_attributes = (a for a in attr_class.attributes if a.has_default)

    def assignment(a: AttrAttribute) -> List[str]:
        return [
            'if self.{name} is not {default}:'.format(name=a.name, default=a.default),
            indent('result[\'{name}\'] = self.{name}'.format(name=a.name))
        ]

    optional_assignments = flatten(assignment(a) for a in optional_attributes)
    body = result_creation + optional_assignments + ['return result']
    return [
        *header,
        *(indent(line) for line in body)
    ]


def dump_attr_class(attr_class: AttrClass) -> List[str]:
    header = ["@attr.s()",
              "class {}:".format(attr_class.name)]
    property_lines = [indent(dump_attr_attribute(attribute)) for attribute in attr_class.attributes]
    load_method_lines = [indent(line) for line in dump_load_method(attr_class)]
    dump_method_lines = [indent(line) for line in dump_dump_method(attr_class)]
    lines = header + property_lines + ONE_EMPTY_LINE + load_method_lines + ONE_EMPTY_LINE + dump_method_lines
    return lines


def dump_schema(schema: SchemaRepresentation) -> str:
    static_lines = [
        'import attr',
        'from typing import Dict, Any, Optional',
        ''
    ]
    all_classes = [schema.root_class] + schema.other_classes
    lines = static_lines + flatten(dump_attr_class(c) + ONE_EMPTY_LINE for c in all_classes)
    return '\n'.join(lines)
