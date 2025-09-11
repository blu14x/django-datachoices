from testapp.tests.choices.base import DataChoicesTestCase


class DictsTestCase(DataChoicesTestCase):
    @classmethod
    def setUpClass(cls):
        members = cls._make_members(lambda id, text: {'id': id, 'text': text})

        cls.Choices = cls._make_choices_class('Choices', members)
        cls.ChoicesWithParams = cls._make_choices_class(
            'Choices', members, value='id', label='text'
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

    def test_eq(self):
        self.assertEqual(self.Choices.FOO, 'FOO')
        self.assertEqual(self.ChoicesWithParams.FOO, 'foo')

    def test_inner_value(self):
        self.assertEqual(dict, type(self.Choices.FOO._value_))
        self.assertEqual(self.Choices.FOO._value_['id'], 'foo')
        self.assertEqual(self.Choices.FOO._value_['text'], 'footastic')

    def test_invalid_value(self):
        with self.assertRaises(ValueError) as errContext:
            members = {'FOO': {'id': 666, 'text': 'footastic'}}
            self._make_choices_class('Choices', members, value='id')

        self.assertEqual(
            "value of <enum 'Choices'> member FOO must be a non-empty string",
            str(errContext.exception),
        )

    def test_duplicated_value(self):
        with self.assertRaises(ValueError) as errContext:
            members = {
                'FOO': {'id': 'foo', 'text': 'footastic'},
                'BAR': {'id': 'foo', 'text': 'barmazing'},
            }
            self._make_choices_class('Choices', members, value='id')

        self.assertEqual(
            "duplicate values found in <enum 'Choices'>: [FOO, BAR] -> foo",
            str(errContext.exception),
        )
