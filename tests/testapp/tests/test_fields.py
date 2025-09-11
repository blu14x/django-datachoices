from dataclasses import dataclass

from datachoices import DataChoiceArrayField, DataChoiceField, DataChoices
from django.test import SimpleTestCase, TestCase
from testapp.choices import ColorChoices, Material, MaterialChoices, Shape, ShapeChoices
from testapp.models import TestModel


@dataclass(frozen=True)
class TestDataClass:
    number: int
    string: str

    def __str__(self):
        return f'{self.number} {self.string}'


class TestDataChoices(TestDataClass, DataChoices):
    ONE = 1, 'one'
    TWO = 2, 'two'
    THREE = 3, 'three'


class FieldTestCase(SimpleTestCase):
    def test_DataChoiceField(self):
        test_data_field = DataChoiceField(choices=TestDataChoices)

        self.assertEqual(TestDataChoices, test_data_field.data_choices)
        self.assertEqual(
            [('ONE', '1 one'), ('TWO', '2 two'), ('THREE', '3 three')],
            test_data_field.choices,
        )

    def test_DataChoiceField_bad_choices(self):
        with self.assertRaises(TypeError) as errContext:
            DataChoiceField()
        self.assertEqual(
            str(errContext.exception),
            'Must provide a DataChoices subclass for choices. Got NoneType',
        )

        with self.assertRaises(TypeError) as errContext:
            DataChoiceField(choices=[('one', 'one')])
        self.assertEqual(
            str(errContext.exception),
            'Must provide a DataChoices subclass for choices. Got list',
        )

        with self.assertRaises(TypeError) as errContext:
            # almost, but need the class itself
            DataChoiceField(choices=TestDataChoices.choices)
        self.assertEqual(
            str(errContext.exception),
            'Must provide a DataChoices subclass for choices. Got list',
        )

    def test_DataChoiceArrayField(self):
        test_data_field = DataChoiceArrayField(choices=TestDataChoices)

        self.assertEqual(TestDataChoices, test_data_field.base_field.data_choices)
        self.assertEqual(
            [('ONE', '1 one'), ('TWO', '2 two'), ('THREE', '3 three')],
            test_data_field.base_field.choices,
        )


class DataChoiceFieldOnModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_instance = TestModel.objects.create(
            color=ColorChoices.RED,
            shape=ShapeChoices.TRIANGLE,
            materials=[MaterialChoices.METAL, MaterialChoices.WOOD],
        )
        # ensure loading from db
        cls.test_instance.refresh_from_db()

    def test_eq(self):
        self.assertEqual(self.test_instance.color, ColorChoices.RED)
        self.assertEqual(self.test_instance.shape, ShapeChoices.TRIANGLE)
        self.assertEqual(
            self.test_instance.materials, [MaterialChoices.METAL, MaterialChoices.WOOD]
        )

    def test_get_FOO_display(self):
        self.assertEqual('Red', self.test_instance.get_color_display())
        self.assertEqual('Triangle', self.test_instance.get_shape_display())
        self.assertEqual('Metal and Wood', self.test_instance.get_materials_display())

    def test_get_FOO_data(self):
        # noinspection PyUnresolvedReferences
        data = self.test_instance.get_shape_data()

        self.assertEqual(Shape, type(data))
        self.assertEqual('Triangle', data.title)
        self.assertEqual(3, data.sides)

        # noinspection PyUnresolvedReferences
        data = self.test_instance.get_materials_data()
        self.assertEqual((Material, Material), (type(data[0]), type(data[1])))
        self.assertEqual(('Metal', 'Wood'), (data[0].title, data[1].title))
        self.assertEqual((0.5, 7.0), (data[0].roughness, data[1].roughness))
