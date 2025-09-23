from functools import partialmethod

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.forms import MultipleChoiceField
from django.utils.encoding import force_str
from django.utils.hashable import make_hashable
from django.utils.text import get_text_list

from .choices import DataChoices


class DataChoicesFieldMixin:  # noqa: D101
    def _check_datachoices(self, choices=None):
        if not isinstance(choices, type) or not issubclass(choices, DataChoices):
            raise TypeError(
                f'Must provide a DataChoices subclass for choices. Got {type(choices).__name__}'
            )
        return choices

    def contribute_to_class(self, cls, name, **kwargs):  # noqa: D102
        display_pname = f'get_{name}_display'
        if display_pname not in cls.__dict__:
            setattr(cls, display_pname, partialmethod(_get_FIELD_display, field=self))
        data_pname = f'get_{name}_data'
        if data_pname not in cls.__dict__:
            setattr(cls, data_pname, partialmethod(_get_FIELD_data, field=self))
        super().contribute_to_class(cls, name, **kwargs)


def _get_FIELD_display(instance, field):
    values = getattr(instance, field.attname)
    if not isinstance(values, list):
        values = [values]

    field = getattr(field, 'base_field', field)
    choices_dict = dict(make_hashable(field.flatchoices))

    strings = [
        force_str(choices_dict.get(make_hashable(value), value), strings_only=True)
        for value in values
    ]
    return get_text_list(strings, last_word='&')


def _get_FIELD_data(instance, field):
    values = getattr(instance, field.attname)
    many = True
    if not isinstance(values, list):
        values = [values] if values else []
        many = False

    dc_field = getattr(field, 'base_field', field)
    data_choices = getattr(dc_field, 'data_choices', None)
    if not data_choices:
        return [] if many else None

    members = []
    for value in values:
        if value in data_choices:
            members.append(data_choices[value])
    if many:
        return [getattr(member, '_value_') for member in members]
    return getattr(members[0], '_value_') if members else None


class DataChoiceField(DataChoicesFieldMixin, models.CharField):  # noqa: D101
    def __init__(self, *args, choices=None, **kwargs):  # noqa: D107
        self.data_choices = self._check_datachoices(choices)
        kwargs['choices'] = self.data_choices.choices
        super().__init__(*args, **kwargs)

    def deconstruct(self):  # noqa: D102
        name, path, args, kwargs = super().deconstruct()
        kwargs['choices'] = self.data_choices
        return name, path, args, kwargs

    def get_prep_value(self, value):  # noqa: D102
        if self.data_choices and isinstance(value, self.data_choices):
            value = value.value
        return super().get_prep_value(value)

    def to_python(self, value):  # noqa: D102
        types = (self.data_choices, str) if self.data_choices else str
        return value if isinstance(value, types) or value is None else str(value)


class DataChoiceArrayField(DataChoicesFieldMixin, ArrayField):  # noqa: D101
    def __init__(self, choices=None, **kwargs):  # noqa: D107
        kwargs['base_field'] = DataChoiceField(choices=self._check_datachoices(choices))
        super().__init__(**kwargs)

    def deconstruct(self):  # noqa: D102
        name, path, args, kwargs = super().deconstruct()
        del kwargs['base_field']
        kwargs['choices'] = getattr(self.base_field, 'data_choices')
        return name, path, args, kwargs

    def formfield(self, **kwargs):  # noqa: D102
        defaults = {
            'form_class': MultipleChoiceField,
            'choices': self.base_field.choices,
        }
        defaults.update(kwargs)
        return super(ArrayField, self).formfield(**defaults)
