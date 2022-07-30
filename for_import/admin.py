from django.contrib import admin
from .models import FixtureFile


@admin.register(FixtureFile)
class FixtureFileAdmin(admin.ModelAdmin):
    list_display = ("id", "file", "name", "status", "priority", "extension")
