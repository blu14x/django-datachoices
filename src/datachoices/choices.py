import enum
from collections.abc import Mapping

from django.db.models.enums import Choices, ChoicesType
from django.utils.version import PY311

if PY311:
    from enum import property as enum_property
else:
    from types import DynamicClassAttribute as enum_property


def validate_data_choices_enum(enumeration):  # noqa: D103
    value_member_map = {}
    for name, member in enumeration.__members__.items():
        if not isinstance(member.value, str) or not member.value:
            raise ValueError(
                f'value of {enumeration} member {name} must be a non-empty string'
            )

        value_member_map.setdefault(member.value, []).append(name)
    duplicates = {
        value: members
        for value, members in value_member_map.items()
        if len(members) > 1
    }
    if duplicates:
        alias_details = ', '.join(
            [
                f'[{", ".join(aliases)}] -> {value}'
                for value, aliases in duplicates.items()
            ]
        )
        raise ValueError(f'duplicate values found in {enumeration}: {alias_details}')

    return enumeration


class DataChoicesMeta(ChoicesType):
    """Modified ChoicesType metaclass for DataChoices."""

    def __new__(  # noqa: D102
        metacls, classname, bases, class_dict, label='', value='', **kwargs
    ):
        class_dict['__member_label__'] = label
        class_dict['__member_value__'] = value
        cls = enum.EnumType.__new__(metacls, classname, bases, class_dict, **kwargs)
        return validate_data_choices_enum(cls)


class DataChoices(Choices, metaclass=DataChoicesMeta):
    """Class for creating enumerated choices bound to dataclass instances."""

    __member_label__: str
    __member_value__: str

    def __init_subclass__(cls, **kwargs):  # noqa: D105
        cls.__eq__ = lambda self, other: self.value == other
        cls.__hash__ = lambda self: hash(self.value)

    @enum_property
    def value(self):  # noqa: D102
        return self._resolve_choice_property(self.__member_value__)

    @enum_property
    def label(self):  # noqa: D102
        default_attr = None
        if isinstance(self._value_, type):
            default_attr = '__name__'
        elif type(self._value_).__str__ is not object.__str__:
            default_attr = '__str__'

        return self._resolve_choice_property(self.__member_label__, default_attr)

    def _resolve_choice_property(self, attr=None, default_attr=None):
        if attr is None:
            return self._name_
        if isinstance(self._value_, Mapping):
            return self._value_.get(attr) if attr else self._name_

        if attr:
            attr_value = getattr(self._value_, attr)
        elif default_attr:
            attr_value = getattr(self._value_, default_attr, self._name_)
        else:
            attr_value = self._name_
        return attr_value() if callable(attr_value) else attr_value
