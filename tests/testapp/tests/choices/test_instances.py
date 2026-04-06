from django.test import SimpleTestCase
from testapp.tests.choices.base import DCTestMixin


class ClassInstancesTestCase(DCTestMixin, SimpleTestCase):
    class SomeClass:
        def __init__(self, _id, text, number):
            self.id = _id
            self.text = text
            self.number = number
            self.same = 'same'

        def __str__(self):
            return f'{self.text} (id: "{self.id}")'

    @classmethod
    def _make_member(cls, *args, **kwargs):
        return cls.SomeClass(*args)

    def test_labels(self):
        # on instances, defaults to __str__
        self.assertLabels(
            self._make_choices_class(),
            ['footastic (id: "foo")', 'barmazing (id: "bar")', 'bazacular (id: "baz")'],
        )
        self.assertLabels(
            self._make_choices_class(label='text'),
            ['footastic', 'barmazing', 'bazacular'],
        )
        self.assertLabels(self._make_choices_class(label=None), ['FOO', 'BAR', 'BAZ'])

    def test_inner_value(self):
        choices = self._make_choices_class()
        self.assertTrue(isinstance(choices.FOO._value_, self.SomeClass))
        self.assertEqual('foo', choices.FOO._value_.id)
        self.assertEqual('footastic', choices.FOO._value_.text)
