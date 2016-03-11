import os

from django.core import checks


def select2_submodule_check(app_configs, **kwargs):
    errors = []
    select2 = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'static/autocomplete_light/vendor/select2/dist/js/select2.min.js'
    )

    if not os.path.exists(select2):
        errors.append(
            checks.Error(
                'Select2 static files not checked out',
                hint='Run git submodule update --init in DAL',
                id='dal_select2.E001',
            )
        )

    return errors
