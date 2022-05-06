from django.templatetags.static import static
from django.urls import reverse
from jinja2 import Environment
from django.utils.translation import gettext, ngettext


def environment(**options):
    env = Environment(**options, extensions=['jinja2.ext.i18n'])
    env.install_gettext_callables(gettext=gettext, ngettext=ngettext, newstyle=True)
    env.globals.update({
        'static': static,
        'url': reverse,
    })


    return env