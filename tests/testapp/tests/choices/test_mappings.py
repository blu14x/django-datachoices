from django.test import SimpleTestCase
from testapp.tests.choices.base import DCTestMixin


class MappingsTestCase(DCTestMixin, SimpleTestCase):
    @classmethod
    def _make_member(cls, *args, **kwargs):
        _id, text, number = args
        return {'id': _id, 'text': text, 'number': number, 'same': 'same'}

    def test_labels(self):
        self.assertLabels(self._make_choices_class(), ['FOO', 'BAR', 'BAZ'])
        self.assertLabels(
            self._make_choices_class(label='text'),
            ['footastic', 'barmazing', 'bazacular'],
        )
        self.assertLabels(self._make_choices_class(label=None), ['FOO', 'BAR', 'BAZ'])

    def test_inner_value(self):
        choices = self._make_choices_class()
        self.assertTrue(isinstance(choices.FOO._value_, dict))
        self.assertEqual(
            'foo',
            choices.FOO._value_['id'],
        )
        self.assertEqual(
            'footastic',
            choices.FOO._value_['text'],
        )
