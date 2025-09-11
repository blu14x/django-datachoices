from django.contrib import admin
from testapp.models import TestModel


@admin.register(TestModel)
class TestModelAdmin(admin.ModelAdmin):
    readonly_fields = [  # noqa: RUF012
        'get_shape_display',
        'get_shape_data',
        'get_materials_display',
        'get_materials_data',
    ]
