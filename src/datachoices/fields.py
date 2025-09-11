from functools import partialmethod

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.forms import MultipleChoiceField
from django.utils.encoding import force_str
from django.utils.hashable import make_hashable
from django.utils.text import get_text_list
from django.utils.translation import gettext_lazy as _

from .choices import DataChoices


def _get_FIELD_data(self, field):
    data_choices = getattr(field, 'data_choices', None)
    if not data_choices:
        return None

    value = getattr(self, field.attname)
    try:
        member = data_choices[value]
    except KeyError:
        return None

    return getattr(member, '_value_')


def _get_FIELD_data_array(self, field):
    data_choices = getattr(field.base_field, 'data_choices', None)
    if not data_choices:
        return []

    values = getattr(self, field.attname)
    if not values:
        return []

    members = []
    for value in values:
        try:
            members.append(data_choices[value])
        except KeyError:
            return None

    return [getattr(member, '_value_') for member in members]


def _get_FIELD_display_array(self, field):
    values = getattr(self, field.attname)
    if not values:
        return ''

    choices_dict = dict(make_hashable(field.base_field.flatchoices))
    strings = [
        force_str(choices_dict.get(make_hashable(value), value), strings_only=True)
        for value in values
    ]
    return get_text_list(strings, last_word=_('and'))


class DataChoiceField(models.CharField):  # noqa: D101
    def __init__(self, *args, choices=None, **kwargs):  # noqa: D107
        if not isinstance(choices, type) or not issubclass(choices, DataChoices):
            raise TypeError(
                f'Must provide a DataChoices subclass for choices. Got {type(choices).__name__}'
            )

        self.data_choices = choices
        kwargs['choices'] = choices.choices
        super().__init__(*args, **kwargs)

    def deconstruct(self):  # noqa: D102
        name, path, args, kwargs = super().deconstruct()
        kwargs['choices'] = self.data_choices
        return name, path, args, kwargs

    def get_prep_value(self, value):  # noqa: D102
        if isinstance(value, self.data_choices):
            value = value.value
        return super().get_prep_value(value)

    def contribute_to_class(self, cls, name, **kwargs):  # noqa: D102
        super().contribute_to_class(cls, name, **kwargs)
        self._add_get_FIELD_data(cls)

    def _add_get_FIELD_data(self, cls):
        prop_name = f'get_{self.name}_data'
        if prop_name not in cls.__dict__:
            setattr(
                cls,
                prop_name,
                partialmethod(_get_FIELD_data, field=self),
            )


class DataChoiceArrayField(ArrayField):  # noqa: D101
    def __init__(self, choices=None, **kwargs):  # noqa: D107
        if not isinstance(choices, type) or not issubclass(choices, DataChoices):
            raise TypeError(
                f'Must provide a DataChoices subclass for choices. Got {type(choices).__name__}'
            )
        kwargs['base_field'] = DataChoiceField(choices=choices)
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

    def contribute_to_class(self, cls, name, **kwargs):  # noqa: D102
        super().contribute_to_class(cls, name, **kwargs)
        self._add_get_FIELD_data(cls)
        self._add_get_FIELD_display(cls)

    def _add_get_FIELD_data(self, cls):
        prop_name = f'get_{self.name}_data'
        if prop_name not in cls.__dict__:
            setattr(
                cls,
                prop_name,
                partialmethod(_get_FIELD_data_array, field=self),
            )

    def _add_get_FIELD_display(self, cls):
        prop_name = f'get_{self.name}_display'
        if prop_name not in cls.__dict__:
            setattr(
                cls,
                prop_name,
                partialmethod(_get_FIELD_display_array, field=self),
            )
