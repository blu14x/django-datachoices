import enum
from collections.abc import Mapping

from django.db.models.enums import Choices, ChoicesType
from django.utils.functional import Promise
from django.utils.version import PY311

if PY311:
    from enum import property as enum_property
else:
    from types import DynamicClassAttribute as enum_property


class DataChoicesMeta(ChoicesType):
    """Metaclass for creating DataChoices."""

    class Auto:
        pass

    def __new__(  # noqa: D102
        metacls, classname, bases, class_dict, label=Auto, value=Auto, **kwargs
    ):
        class_dict['__member_value_attr__'] = value
        class_dict['__member_label_attr__'] = label
        cls = enum.EnumType.__new__(metacls, classname, bases, class_dict, **kwargs)
        return metacls._validate_data_choices_enum(cls)

    @staticmethod
    def _validate_data_choices_enum(enumeration):
        value_map = {}
        label_map = {}

        for name, member in enumeration.__members__.items():
            for prop, acc, types in [
                ('value', value_map, (str,)),
                ('label', label_map, (str, Promise)),
            ]:
                try:
                    value = getattr(member, prop)
                except (AttributeError, KeyError) as e:
                    raise ValueError(
                        f'{prop} property is invalid for {enumeration} member {name}'
                    ) from e
                if not value or not isinstance(value, types):
                    raise ValueError(
                        f'{prop} property of {enumeration} member {name} must be a non-empty string'
                    )
                acc.setdefault(str(value), []).append(member.name)
        for prop, acc in [('value', value_map), ('label', label_map)]:
            duplicate_values = {
                value: members for value, members in acc.items() if len(members) > 1
            }
            if duplicate_values:
                alias_details = [
                    f'[{", ".join(str(a) for a in aliases)}] -> {value}'
                    for value, aliases in duplicate_values.items()
                ]
                raise ValueError(
                    f'duplicate {prop}s found in {enumeration}: {", ".join(alias_details)}'
                )
        return enumeration


class DataChoices(Choices, metaclass=DataChoicesMeta):
    """Class for creating enumerated choices of complex data."""

    __member_value_attr__: str
    __member_label_attr__: str

    def __init_subclass__(cls, **kwargs):  # noqa: D105
        cls.__eq__ = lambda self, other: self.value == other
        cls.__hash__ = lambda self: hash(self.value)

    @enum_property
    def value(self):  # noqa: D102
        attr = self.__member_value_attr__
        if attr == DataChoicesMeta.Auto:
            attr = None
        return self._resolve_attr(attr)

    @enum_property
    def label(self):  # noqa: D102
        attr = self.__member_label_attr__
        if attr == DataChoicesMeta.Auto:
            if isinstance(self._value_, type):
                attr = '__name__'
            elif type(self._value_).__str__ is not object.__str__:
                attr = '__str__'
            else:
                attr = None
        return self._resolve_attr(attr)

    def _resolve_attr(self, attr: None | str):
        if not attr:
            attr_value = self._name_
        else:
            if isinstance(self._value_, Mapping):
                attr_value = self._value_[attr]
            else:
                attr_value = getattr(self._value_, attr)
        return attr_value() if callable(attr_value) else attr_value
