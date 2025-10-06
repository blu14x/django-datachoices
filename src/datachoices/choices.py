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
    label_member_map = {}

    def _check_property_is_valid(
        _member_name,
        _member,
        property_member_map,
        property_name: str,
        property_attribute: str,
    ):
        try:
            value = getattr(_member, property_name)
        except (AttributeError, KeyError):
            raise ValueError(
                f'{property_name} property "{getattr(enumeration, property_attribute)}" is invalid for {enumeration} member {_member_name}'
            )
        if not value or not isinstance(value, str):
            raise ValueError(
                f'{property_name} property "{getattr(enumeration, property_attribute)}" of {enumeration} member {_member_name} must be a non-empty string'
            )
        property_member_map.setdefault(value, []).append(_member_name)

    def _check_property_duplicates(
        property_member_map,
        property_name: str,
    ):
        duplicate_values = {
            value: members
            for value, members in property_member_map.items()
            if len(members) > 1
        }
        if duplicate_values:
            alias_details = ', '.join(
                [
                    f'[{", ".join(aliases)}] -> {value}'
                    for value, aliases in duplicate_values.items()
                ]
            )
            raise ValueError(
                f'duplicate {property_name}s found in {enumeration}: {alias_details}'
            )

    for name, member in enumeration.__members__.items():
        _check_property_is_valid(
            name, member, value_member_map, 'value', '__member_value__'
        )
        _check_property_is_valid(
            name, member, label_member_map, 'label', '__member_label__'
        )

    _check_property_duplicates(value_member_map, 'value')
    _check_property_duplicates(label_member_map, 'label')

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
        attr = self.__member_value__
        return self._resolve_choice_property(attr)

    @enum_property
    def label(self):  # noqa: D102
        attr = self.__member_label__
        if attr == '':
            if isinstance(self._value_, type):
                attr = '__name__'
            elif type(self._value_).__str__ is not object.__str__:
                attr = '__str__'
        return self._resolve_choice_property(attr)

    def _resolve_choice_property(self, attr: None | str):
        if attr:
            if isinstance(self._value_, Mapping):
                attr_value = self._value_[attr]
            else:
                attr_value = getattr(self._value_, attr)
        else:
            attr_value = self._name_
        return attr_value() if callable(attr_value) else attr_value
