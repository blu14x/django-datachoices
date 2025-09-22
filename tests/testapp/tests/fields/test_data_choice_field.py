from datachoices import DataChoiceField
from django.core.exceptions import ValidationError
from django.test import TestCase
from testapp.choices import ShapeChoices
from testapp.models import DataChoiceTestModel


class DataChoiceFieldTestCase(TestCase):
    def test_choices_arg(self):
        with self.assertRaises(TypeError) as errCtx:
            DataChoiceField()
        self.assertEqual(
            'Must provide a DataChoices subclass for choices. Got NoneType',
            str(errCtx.exception),
        )

        with self.assertRaises(TypeError) as errCtx:
            DataChoiceField(choices=[])
        self.assertEqual(
            'Must provide a DataChoices subclass for choices. Got list',
            str(errCtx.exception),
        )

        with self.assertRaises(TypeError) as errCtx:
            DataChoiceField(choices=ShapeChoices.choices)
        self.assertEqual(
            'Must provide a DataChoices subclass for choices. Got list',
            str(errCtx.exception),
        )

        field = DataChoiceField(choices=ShapeChoices)
        self.assertEqual(field.data_choices, ShapeChoices)
        self.assertEqual(field.choices, ShapeChoices.choices)

    def test_model(self):
        instance = DataChoiceTestModel()

        with self.assertRaises(ValidationError) as errCtx:
            instance.clean_fields()
        self.assertDictEqual(
            {'shape': ['This field cannot be blank.']},
            errCtx.exception.message_dict,
        )

        instance.shape = 'this_so_invalid'
        with self.assertRaises(ValidationError) as errCtx:
            instance.clean_fields()
        self.assertDictEqual(
            {'shape': ["Value 'this_so_invalid' is not a valid choice."]},
            errCtx.exception.message_dict,
        )

        instance.shape = ShapeChoices.PENTAGON
        instance.clean_fields()
        instance.save()
        instance.refresh_from_db()

        self.assertEqual(ShapeChoices.PENTAGON, instance.shape)
        self.assertEqual(ShapeChoices.SQUARE, instance.shape_default)
        self.assertEqual('', instance.shape_non_required)

    def test_model_contributions(self):
        instance = DataChoiceTestModel(shape=ShapeChoices.PENTAGON)

        self.assertEqual('Pentagon', instance.get_shape_display())
        self.assertEqual('Square', instance.get_shape_default_display())
        self.assertEqual('', instance.get_shape_non_required_display())

        self.assertEqual(ShapeChoices.PENTAGON._value_, instance.get_shape_data())
        self.assertEqual(ShapeChoices.SQUARE._value_, instance.get_shape_default_data())
        self.assertEqual(None, instance.get_shape_non_required_data())

    def test_model_contributions_weird_cases(self):
        instance = DataChoiceTestModel.objects.create(shape=ShapeChoices.PENTAGON)
        shape_field = instance._meta.get_field('shape')

        # ! need to revert for other tests
        shape_field.choices = []
        shape_field.data_choices = None

        # actually django behaviour
        self.assertEqual('ShapeChoices.PENTAGON', instance.get_shape_display())
        self.assertEqual(None, instance.get_shape_data())

        # revert
        shape_field.choices = ShapeChoices.choices
        shape_field.data_choices = ShapeChoices
