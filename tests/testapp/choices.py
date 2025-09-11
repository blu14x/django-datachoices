from dataclasses import dataclass

from datachoices import DataChoices
from django.db.models import TextChoices


class ColorChoices(TextChoices):
    RED = 'RED', 'Red'
    GREEN = 'GREEN', 'Green'
    BLUE = 'BLUE', 'Blue'


@dataclass(frozen=True)
class Shape:
    title: str
    sides: int

    def __str__(self):
        return self.title


class ShapeChoices(Shape, DataChoices):
    TRIANGLE = 'Triangle', 3
    SQUARE = 'Square', 4
    PENTAGON = 'Pentagon', 5
    HEXAGON = 'Hexagon', 6


@dataclass(frozen=True)
class Material:
    title: str
    roughness: float

    def __str__(self):
        return self.title


class MaterialChoices(Material, DataChoices):
    METAL = 'Metal', 0.5
    PLASTIC = 'Plastic', 1.0
    STONE = 'Stone', 4.0
    WOOD = 'Wood', 7.0
