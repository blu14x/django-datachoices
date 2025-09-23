from django.contrib import admin
from testapp.models import (
    DataChoiceArrayTestModel,
    DataChoiceTestModel,
)


@admin.register(DataChoiceTestModel)
class DataChoiceTestModelAdmin(admin.ModelAdmin):
    pass


@admin.register(DataChoiceArrayTestModel)
class DataChoiceArrayTestModelAdmin(admin.ModelAdmin):
    pass
