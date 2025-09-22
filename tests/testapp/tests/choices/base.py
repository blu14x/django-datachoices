from datachoices import DataChoices
from django.test import SimpleTestCase

__unittest = True


class DataChoicesTestCase(SimpleTestCase):
    @staticmethod
    def _make_choices_class(name, members: dict, member_type=None, **kwargs):
        bases = (member_type, DataChoices) if member_type else (DataChoices,)
        metaclass = type(DataChoices)
        class_dict = metaclass.__prepare__(name, bases)
        class_dict.update(members)
        return metaclass(name, bases, class_dict, **kwargs)

    @staticmethod
    def _make_members(make_member=None):
        members = {
            'FOO': ('foo', 'footastic'),
            'BAR': ('bar', 'barmazing'),
            'BAZ': ('baz', 'bazacular'),
        }
        if make_member:
            return {
                member_name: make_member(*args) for member_name, args in members.items()
            }
        return members

    def assertChoices(
        self, choices_class: type[DataChoices], expected_choices: list[tuple[str, str]]
    ):
        self.assertEqual(expected_choices, choices_class.choices)
