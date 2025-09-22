from datachoices import DataChoiceArrayField, DataChoiceField
from django.db import models
from testapp.choices import MaterialChoices, ShapeChoices


class DataChoiceTestModel(models.Model):  # noqa: DJ008
    """A model for testing DataChoiceField."""

    shape = DataChoiceField(choices=ShapeChoices)
    shape_default = DataChoiceField(choices=ShapeChoices, default=ShapeChoices.SQUARE)
    shape_non_required = DataChoiceField(choices=ShapeChoices, default='', blank=True)


def _materials_default():
    return [MaterialChoices.METAL, MaterialChoices.WOOD]


class DataChoiceArrayTestModel(models.Model):  # noqa: DJ008
    """A model for testing the DataChoiceArrayField."""

    materials = DataChoiceArrayField(choices=MaterialChoices)
    materials_default = DataChoiceArrayField(
        choices=MaterialChoices,
        default=_materials_default,
    )
    materials_non_required = DataChoiceArrayField(
        choices=MaterialChoices, default=list, blank=True
    )
