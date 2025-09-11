from testapp.tests.choices.base import DataChoicesTestCase


class ClassInstancesTestCase(DataChoicesTestCase):
    class SomeClass:
        def __init__(self, _id, text):
            self.id = _id
            self.text = text

    class SomeStrClass(SomeClass):
        def __str__(self):
            return f'{self.text} (id: "{self.id}")'

    @classmethod
    def setUpClass(cls):
        members = cls._make_members(lambda *args: cls.SomeClass(*args))
        members_with_str = cls._make_members(lambda *args: cls.SomeStrClass(*args))

        cls.Choices = cls._make_choices_class('Choices', members)
        cls.ChoicesWithParams = cls._make_choices_class(
            'Choices', members, value='id', label='text'
        )
        cls.ChoicesWithStr = cls._make_choices_class('ChoicesWithStr', members_with_str)

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
        self.assertEqual('FOO', self.Choices.FOO)
        self.assertEqual('foo', self.ChoicesWithParams.FOO)

    def test_inner_value(self):
        self.assertEqual(self.SomeClass, type(self.Choices.FOO._value_))
        self.assertEqual('foo', self.Choices.FOO._value_.id)
        self.assertEqual('footastic', self.Choices.FOO._value_.text)

    def test_invalid_value(self):
        with self.assertRaises(ValueError) as errContext:
            members = {'FOO': self.SomeClass(42, 'footastic')}
            self._make_choices_class('Choices', members, value='id')

        self.assertEqual(
            "value of <enum 'Choices'> member FOO must be a non-empty string",
            str(errContext.exception),
        )

    def test_duplicated_value(self):
        with self.assertRaises(ValueError) as errContext:
            members = {
                'FOO': self.SomeClass('foo', 'footastic'),
                'BAR': self.SomeClass('foo', 'barmazing'),
            }
            self._make_choices_class('Choices', members, value='id')

        self.assertEqual(
            "duplicate values found in <enum 'Choices'>: [FOO, BAR] -> foo",
            str(errContext.exception),
        )
