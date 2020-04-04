from abc import ABC
from typing import List, Type, Optional

import attr


@attr.s()
class AttrAttribute:
    name = attr.ib(type=str)
    type = attr.ib(type=str)
    default = attr.ib(type=Optional[str], default=None)

    @property
    def has_default(self) -> bool:
        return self.default is not None


@attr.s()
class AttrClass:
    name = attr.ib(type=str)
    attributes = attr.ib(type=List[AttrAttribute])


@attr.s()
class SchemaRepresentation:
    root_class = attr.ib(type=AttrClass)
    other_classes = attr.ib(type=List[AttrClass])

