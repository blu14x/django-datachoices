from datachoices import DataChoiceArrayField
from django.core.exceptions import ValidationError
from django.forms import MultipleChoiceField
from django.test import TestCase
from testapp.choices import MaterialChoices, ShapeChoices
from testapp.models import DataChoiceArrayTestModel


class DataChoiceFieldTestCase(TestCase):
    def test_choices_arg(self):
        with self.assertRaises(TypeError) as errCtx:
            DataChoiceArrayField()
        self.assertEqual(
            'Must provide a DataChoices subclass for choices. Got NoneType',
            str(errCtx.exception),
        )

        with self.assertRaises(TypeError) as errCtx:
            DataChoiceArrayField(choices=[])
        self.assertEqual(
            'Must provide a DataChoices subclass for choices. Got list',
            str(errCtx.exception),
        )

        with self.assertRaises(TypeError) as errCtx:
            DataChoiceArrayField(choices=ShapeChoices.choices)
        self.assertEqual(
            'Must provide a DataChoices subclass for choices. Got list',
            str(errCtx.exception),
        )

        field = DataChoiceArrayField(choices=ShapeChoices)
        self.assertEqual(field.base_field.data_choices, ShapeChoices)
        self.assertEqual(field.base_field.choices, ShapeChoices.choices)

    def test_form_field(self):
        field = DataChoiceArrayField(choices=ShapeChoices)

        form_field = field.formfield()
        self.assertTrue(isinstance(form_field, MultipleChoiceField))
        self.assertEqual(form_field.choices, ShapeChoices.choices)

    def test_model(self):
        instance = DataChoiceArrayTestModel()

        with self.assertRaises(ValidationError) as errCtx:
            instance.clean_fields()
        self.assertDictEqual(
            {'materials': ['This field cannot be null.']},
            errCtx.exception.message_dict,
        )

        instance.materials = ['this_so_invalid', 'METAL']
        with self.assertRaises(ValidationError) as errCtx:
            instance.clean_fields()
        self.assertDictEqual(
            {
                'materials': [
                    "Item 1 in the array did not validate: Value 'this_so_invalid' is not a valid choice."
                ]
            },
            errCtx.exception.message_dict,
        )

        instance.materials = [MaterialChoices.PLASTIC, MaterialChoices.METAL]
        instance.clean_fields()
        instance.save()
        instance.refresh_from_db()

        self.assertEqual(
            [MaterialChoices.PLASTIC, MaterialChoices.METAL], instance.materials
        )
        self.assertEqual(
            [MaterialChoices.METAL, MaterialChoices.WOOD], instance.materials_default
        )
        self.assertEqual([], instance.materials_non_required)

    def test_model_contributions(self):
        instance = DataChoiceArrayTestModel(materials=[MaterialChoices.WOOD])

        self.assertEqual('Wood', instance.get_materials_display())
        self.assertEqual('Metal & Wood', instance.get_materials_default_display())
        self.assertEqual('', instance.get_materials_non_required_display())

        self.assertEqual([MaterialChoices.WOOD._value_], instance.get_materials_data())
        self.assertEqual(
            [MaterialChoices.METAL._value_, MaterialChoices.WOOD._value_],
            instance.get_materials_default_data(),
        )
        self.assertEqual([], instance.get_materials_non_required_data())

    def test_model_contributions_weird_cases(self):
        instance = DataChoiceArrayTestModel(
            materials=[MaterialChoices.WOOD, MaterialChoices.PLASTIC]
        )
        shape_field = instance._meta.get_field('materials')

        # ! need to revert for other tests
        shape_field.base_field.choices = []
        shape_field.base_field.data_choices = None

        # actually django behaviour
        self.assertEqual(
            'MaterialChoices.WOOD & MaterialChoices.PLASTIC',
            instance.get_materials_display(),
        )
        self.assertEqual([], instance.get_materials_data())

        # revert
        shape_field.base_field.choices = MaterialChoices.choices
        shape_field.base_field.data_choices = MaterialChoices
