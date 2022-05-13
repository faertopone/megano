from django.templatetags.static import static
from django.urls import reverse
from django.utils import translation
from jinja2 import Environment


def environment(**options):
    env = Environment(extensions=["jinja2.ext.i18n"], **options)

    # Подробнее о подключении расширений
    # https://jinja.palletsprojects.com/en/3.0.x/extensions/
    env.install_gettext_translations(translation)
    env.globals.update({
        'static': static,
        'url': reverse,
    })
    return env
