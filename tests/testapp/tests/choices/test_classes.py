from testapp.tests.choices.base import DataChoicesTestCase


class ClassesTestCase(DataChoicesTestCase):
    class FooClass:
        id = 'foo'
        text = 'footastic'

    class BarClass:
        id = 'bar'
        text = 'barmazing'

    class BazClass:
        id = 'baz'
        text = 'bazacular'

    @classmethod
    def setUpClass(cls):
        members = {'FOO': cls.FooClass, 'BAR': cls.BarClass, 'BAZ': cls.BazClass}

        cls.Choices = cls._make_choices_class('Choices', members)
        cls.ChoicesWithParams = cls._make_choices_class(
            'Choices', members, value='id', label='text'
        )
        cls.ChoicesNoDefaultLabel = cls._make_choices_class(
            'ChoicesNoDefaultLabel', members, label=None
        )

    def test_basic(self):
        # on classes, defaults for __name__ for the label
        self.assertChoices(
            self.Choices,
            [('FOO', 'FooClass'), ('BAR', 'BarClass'), ('BAZ', 'BazClass')],
        )

    def test_params(self):
        self.assertChoices(
            self.ChoicesWithParams,
            [('foo', 'footastic'), ('bar', 'barmazing'), ('baz', 'bazacular')],
        )

    def test_label_none(self):
        self.assertChoices(
            self.ChoicesNoDefaultLabel,
            [('FOO', 'FOO'), ('BAR', 'BAR'), ('BAZ', 'BAZ')],
        )

    def test_eq(self):
        self.assertEqual('FOO', self.Choices.FOO)
        self.assertEqual('foo', self.ChoicesWithParams.FOO)

    def test_inner_value(self):
        self.assertEqual(self.FooClass, self.Choices.FOO._value_)
        self.assertEqual('foo', self.Choices.FOO._value_.id)
        self.assertEqual('footastic', self.Choices.FOO._value_.text)

    def test_invalid_value(self):
        class NumberClass:
            id = 420
            text = 'one'

        with self.assertRaises(ValueError) as errCtx:
            members = {'FOO': NumberClass}
            self._make_choices_class('Choices', members, value='id')

        self.assertEqual(
            "value of <enum 'Choices'> member FOO must be a non-empty string",
            str(errCtx.exception),
        )

    def test_duplicated_value(self):
        with self.assertRaises(ValueError) as errCtx:
            members = {
                'FOO': self.FooClass,
                'BAR': self.FooClass,
            }
            self._make_choices_class('Choices', members, value='id')

        self.assertEqual(
            "duplicate values found in <enum 'Choices'>: [FOO, BAR] -> foo",
            str(errCtx.exception),
        )
