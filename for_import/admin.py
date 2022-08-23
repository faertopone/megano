from django.contrib import admin

from for_import.models import FixtureFile


@admin.register(FixtureFile)
class FixtureFileAdmin(admin.ModelAdmin):
    list_display = ("id", "file", "name", "status", "priority", "extension")
