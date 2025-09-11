"""
Models for testing django_datachoices fields.
"""

from datachoices import DataChoiceArrayField, DataChoiceField
from django.db import models
from testapp.choices import ColorChoices, MaterialChoices, ShapeChoices


class TestModel(models.Model):  # noqa: DJ008
    """A model for testing DataChoiceField."""

    color = models.CharField(
        choices=ColorChoices,
    )
    shape = DataChoiceField(
        choices=ShapeChoices,
    )
    materials = DataChoiceArrayField(
        choices=MaterialChoices,
    )
