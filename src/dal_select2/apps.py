from django.apps import AppConfig
from django.core import checks

from .checks import select2_submodule_check


class DefaultApp(AppConfig):
    name = 'dal_select2'

    def ready(self):
        checks.register(select2_submodule_check)
