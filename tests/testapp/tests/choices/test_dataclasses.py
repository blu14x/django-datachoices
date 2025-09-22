from dataclasses import dataclass

from testapp.tests.choices.base import DataChoicesTestCase


class DataclassesTestCase(DataChoicesTestCase):
    @dataclass(frozen=True)
    class SomeClass:
        id: str
        text: str

    class SomeStrClass(SomeClass):
        def __str__(self):
            return f'{self.text} (id: "{self.id}")'

    @classmethod
    def setUpClass(cls):
        members = cls._make_members()

        cls.Choices = cls._make_choices_class('Choices', members, cls.SomeClass)
        cls.ChoicesWithParams = cls._make_choices_class(
            'Choices', members, cls.SomeClass, value='id', label='text'
        )
        cls.ChoicesWithStr = cls._make_choices_class(
            'ChoicesWithStr', members, cls.SomeStrClass
        )

    def test_basic(self):
        self.assertChoices(
            self.Choices, [('FOO', 'FOO'), ('BAR', 'BAR'), ('BAZ', 'BAZ')]
        )

    def test_params(self):
        self.assertChoices(
            self.ChoicesWithParams,
            [('foo', 'footastic'), ('bar', 'barmazing'), ('baz', 'bazacular')],
        )

    def test_label_from_str(self):
        self.assertChoices(
            self.ChoicesWithStr,
            [
                ('FOO', 'footastic (id: "foo")'),
                ('BAR', 'barmazing (id: "bar")'),
                ('BAZ', 'bazacular (id: "baz")'),
            ],
        )

    def test_eq(self):
        self.assertEqual(self.Choices.FOO, 'FOO')
        self.assertEqual(self.ChoicesWithParams.FOO, 'foo')

    def test_inner_value(self):
        self.assertTrue(isinstance(self.Choices.FOO._value_, self.SomeClass))
        self.assertEqual(self.Choices.FOO._value_.id, 'foo')
        self.assertEqual(self.Choices.FOO._value_.text, 'footastic')

    def test_invalid_value(self):
        with self.assertRaises(ValueError) as errCtx:
            members = {'FOO': (69, 'footastic')}
            self._make_choices_class('Choices', members, self.SomeClass, value='id')

        self.assertEqual(
            "value of <enum 'Choices'> member FOO must be a non-empty string",
            str(errCtx.exception),
        )

    def test_duplicated_value(self):
        with self.assertRaises(ValueError) as errCtx:
            members = {
                'FOO': ('foo', 'footastic'),
                'BAR': ('foo', 'barmazing'),
            }
            self._make_choices_class('Choices', members, self.SomeClass, value='id')

        self.assertEqual(
            "duplicate values found in <enum 'Choices'>: [FOO, BAR] -> foo",
            str(errCtx.exception),
        )
