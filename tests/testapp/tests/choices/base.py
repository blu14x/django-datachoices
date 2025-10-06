from datachoices import DataChoices
from django.test import SimpleTestCase

__unittest = True


class DataChoicesTestCase(SimpleTestCase):
    __test__ = False

    def __init_subclass__(cls, **kwargs):
        cls.__test__ = True

    member_type = None
    members_dict = {  # noqa: RUF012
        'FOO': ('foo', 'footastic', 1),
        'BAR': ('bar', 'barmazing', 2),
        'BAZ': ('baz', 'bazacular', 3),
    }

    @classmethod
    def _make_choices_class(cls, members_dict=None, **kwargs):
        members = {
            member_name: cls._make_member(*args)
            for member_name, args in (members_dict or cls.members_dict).items()
        }
        class_name = 'Choices'
        bases = (cls.member_type, DataChoices) if cls.member_type else (DataChoices,)
        metaclass = type(DataChoices)
        class_dict = metaclass.__prepare__(class_name, bases)
        class_dict.update(members)
        return metaclass(class_name, bases, class_dict, **kwargs)

    @classmethod
    def _make_member(cls, *args):
        return args

    def assertChoices(
        self, choices_class: type[DataChoices], expected_choices: list[tuple[str, str]]
    ):
        self.assertEqual(expected_choices, choices_class.choices)

    def assertLabels(
        self, choices_class: type[DataChoices], expected_labels: list[str]
    ):
        self.assertEqual(expected_labels, choices_class.labels)

    def assertValues(self, choices_class: type[DataChoices], expected_values: list):
        self.assertEqual(expected_values, choices_class.values)

    # Shared tests

    def test_eq(self):
        self.assertEqual('FOO', self._make_choices_class().FOO)
        self.assertEqual('foo', self._make_choices_class(value='id').FOO)

    def test_values(self):
        self.assertValues(self._make_choices_class(), ['FOO', 'BAR', 'BAZ'])
        self.assertValues(self._make_choices_class(value='id'), ['foo', 'bar', 'baz'])
        self.assertValues(self._make_choices_class(value=None), ['FOO', 'BAR', 'BAZ'])

    def test_invalid_values(self):
        with self.assertRaisesMessage(
            ValueError,
            'value property "not_a_property" is invalid for <enum \'Choices\'> member FOO',
        ):
            self._make_choices_class(value='not_a_property')

        with self.assertRaisesMessage(
            ValueError,
            'value property "number" of <enum \'Choices\'> member FOO must be a non-empty string',
        ):
            self._make_choices_class(value='number')

        with self.assertRaisesMessage(
            ValueError,
            "duplicate values found in <enum 'Choices'>: [FOO, BAR, BAZ] -> same",
        ):
            self._make_choices_class(value='same')

    def test_invalid_labels(self):
        with self.assertRaisesMessage(
            ValueError,
            'label property "not_a_property" is invalid for <enum \'Choices\'> member FOO',
        ):
            self._make_choices_class(label='not_a_property')

        with self.assertRaisesMessage(
            ValueError,
            'label property "number" of <enum \'Choices\'> member FOO must be a non-empty string',
        ):
            self._make_choices_class(label='number')

        with self.assertRaisesMessage(
            ValueError,
            "duplicate labels found in <enum 'Choices'>: [FOO, BAR, BAZ] -> same",
        ):
            self._make_choices_class(label='same')
