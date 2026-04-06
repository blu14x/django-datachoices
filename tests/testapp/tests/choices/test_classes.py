from django.test import SimpleTestCase
from testapp.tests.choices.base import DCTestMixin


class ClassesTestCase(DCTestMixin, SimpleTestCase):
    class FooClass:
        id = 'foo'
        text = 'footastic'
        number = 1
        same = 'same'

    class BarClass:
        id = 'bar'
        text = 'barmazing'
        number = 2
        same = 'same'

    class BazClass:
        id = 'baz'
        text = 'bazacular'
        number = 3
        same = 'same'

    members_dict = {  # noqa: RUF012
        'FOO': (FooClass,),
        'BAR': (BarClass,),
        'BAZ': (BazClass,),
    }

    @classmethod
    def _make_member(cls, *args, **kwargs):
        return args[0]

    def test_labels(self):
        # on classes, defaults to __name__
        self.assertLabels(
            self._make_choices_class(), ['FooClass', 'BarClass', 'BazClass']
        )
        self.assertLabels(self._make_choices_class(label=None), ['FOO', 'BAR', 'BAZ'])
        self.assertLabels(
            self._make_choices_class(label='text'),
            ['footastic', 'barmazing', 'bazacular'],
        )

    def test_inner_value(self):
        choices = self._make_choices_class()
        self.assertEqual(self.FooClass, choices.FOO._value_)
        self.assertEqual('foo', choices.FOO._value_.id)
        self.assertEqual('footastic', choices.FOO._value_.text)
