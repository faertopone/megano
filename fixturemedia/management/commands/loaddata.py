import os.path
import shutil

from django.apps import apps
from django.conf import settings
import django.core.management.commands.loaddata
import django.core.serializers
from django.db.models import signals
from django.db.models.fields.files import FileField

# For Python < 3.3
file_not_found_error = getattr(__builtins__, 'FileNotFoundError', IOError)


def models_with_filefields():
    modelclasses = apps.get_models()
    for modelclass in modelclasses:
        if any(isinstance(field, FileField) for field in modelclass._meta.fields):
            yield modelclass


class Command(django.core.management.commands.loaddata.Command):

    def load_images_for_signal(self, sender, **kwargs):
        for fixture_media_path in self.fixture_media_paths:
            shutil.copytree(fixture_media_path, settings.MEDIA_ROOT, dirs_exist_ok=True)

    def handle(self, *fixture_labels, **options):
        self.fixture_labels = fixture_labels

        # Hook up pre_save events for all the apps' models that have FileFields.
        for modelclass in models_with_filefields():
            signals.post_save.connect(self.load_images_for_signal, sender=modelclass)

        fixture_paths = self.find_fixture_paths()
        fixture_media_paths = (os.path.join(path, 'media') for path in fixture_paths)
        fixture_media_paths = [path for path in fixture_media_paths if os.path.isdir(path)]
        self.fixture_media_paths = fixture_media_paths

        return super(Command, self).handle(*fixture_labels, **options)

    def find_fixture_paths(self):
        """Return the full paths to all possible fixture directories."""
        return [os.path.dirname(os.path.abspath(fixture_label)) for fixture_label in self.fixture_labels]
