from dataclasses import dataclass

from datachoices import DataChoices
from django.utils.translation import gettext_lazy as _


@dataclass(frozen=True)
class Shape:
    title: str
    sides: int

    def __str__(self):
        return self.title


class ShapeChoices(Shape, DataChoices):
    TRIANGLE = _('Triangle'), 3
    SQUARE = _('Square'), 4
    PENTAGON = _('Pentagon'), 5
    HEXAGON = _('Hexagon'), 6


@dataclass(frozen=True)
class Material:
    title: str
    roughness: float

    def __str__(self):
        return self.title


class MaterialChoices(Material, DataChoices):
    METAL = _('Metal'), 0.5
    PLASTIC = _('Plastic'), 1.0
    STONE = _('Stone'), 4.0
    WOOD = _('Wood'), 7.0
