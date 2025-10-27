# django datachoices

---
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PyPI - Version](https://img.shields.io/pypi/v/django-datachoices)](https://pypi.org/project/django-datachoices/)


#### Utility for Django to bind field choices with rich data.

Provides two core classes — **DataChoices** and **DataChoiceField** — designed to simplify handling model field choices that are tied to complex data.  

## Install
```sh
pip install django-datachoices
```

## Usage
```python
from datachoices import DataChoices, DataChoiceField
from django.db import models


class GameChoices(DataChoices, label="title"):
    SM64 = {"title": "Super Mario 64", "id": "NAAE", "year": 1996}
    SMS = {"title": "Super Mario Sunshine", "id": "GMSP01", "year": 2002}
    SMG = {"title": "Super Mario Galaxy", "id": "RMGP01", "year": 2007}

class MyModel(models.Model):
    game = DataChoiceField(choices=GameChoices)
```
```python
> instance = MyModel.objects.create(game=GameChoices.SMS)

> instance.game
"SMS"
> instance.get_game_display()
"Super Mario Sunshine"
> instance.get_game_data()
{"title": "Super Mario Sunshine", "id": "GMSP01", "year": 2002}
```

### label / value attribute
The **label** (readable representation, e.g., on select widgets) and the **value** (the actual field value for the database) attributes are set using class arguments:
```python
class GameChoices(DataChoices, label="title", value="id"):
    …
```
```python
> instance.game
"GMSP01"
```
If not specified, the member name (*SM64*, *SMS* or *SMG* in this example) is used as the value. This is fine for most cases.  
However, the label is mostly more interesting for display purposes. If not specified, this defaults to *\_\_str__*, *\_\_name__* or the member name (depending on the type).


```python
from datachoices import DataChoices, DataChoiceField
from django.db import models

from my_app import FooClass, BarClass


class HandlerClassChoices(DataChoices):
    FOO = FooClass
    BAR = BarClass

class MyModel(models.Model):
    handler_class = DataChoiceField(choices=HandlerClassChoices)
```
```python
> instance = MyModel.objects.create(handler_class=HandlerClassChoices.BAR)

> instance.get_handler_class_display()
"BarClass"
```

### Member types
This package is currently tested using **dictionaries**, **classes**, **class instances** and **@dataclass instances** as member types.


```python
# dicts

class DictChoices(DataChoices):
    FOO = {"title": "Foo", "number": 1}
    BAR = {"title": "Bar", "number": 2}
    
# classes

class ClassChoices(DataChoices):
    FOO = FooClass
    BAR = BarClass

# class instances

class InstanceChoices(DataChoices):
    FOO = SomeClass("Foo")
    BAR = SomeClass("Bar")

# instances using dataclass mixin syntax

@dataclass
class SomeMixin:
    title: str
    number: int

class DataclassInstanceChoices(SomeMixin, DataChoices):
    FOO = "Foo", 1
    BAR = "Bar", 2
```

### Multiple choice fields
This package also provides a **DataChoiceArrayField** class that can be used to create multiple choice fields.  
Just be aware, this uses django's *django.contrib.postgres.fields.**ArrayField***. So to use it, you need a postgres database.

```python
from datachoices import DataChoices, DataChoiceArrayField
from django.db import models


class GameChoices(DataChoices, label="title"):
    SM64 = {"title": "Super Mario 64", "id": "NAAE", "year": 1996}
    SMS = {"title": "Super Mario Sunshine", "id": "GMSP01", "year": 2002}
    SMG = {"title": "Super Mario Galaxy", "id": "RMGP01", "year": 2007}

class MyModel(models.Model):
    games = DataChoiceArrayField(choices=GameChoices)
```
```python
> instance = MyModel.objects.create(games=[GameChoices.SM64, GameChoices.SMG])

> instance.get_games_display()
"Super Mario 64 & Super Mario Galaxy"
> instance.get_games_data()
[
    {"title": "Super Mario Sunshine", "id": "GMSP01", "year": 2002},
    {"title": "Super Mario Galaxy", "id": "RMGP01", "year": 2007}
]
```