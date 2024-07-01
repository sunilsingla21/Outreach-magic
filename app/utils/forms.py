from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import SelectField

from app.models import Host
from app.utils.time import parsed_timezones


def get_form_error_string(key: str, errors):
    return f'{key.capitalize().replace("_", " ")}: {". ".join(errors[key])}'


KEYS_TO_IGNORE = ['csrf_token']


def update_data_from_form(obj, form: FlaskForm, keys_to_ignore: list[str] | None = None, filter=None):
    if keys_to_ignore is None:
        keys_to_ignore = []
    keys_to_ignore += KEYS_TO_IGNORE

    for key, value in form.data.items():
        if key in keys_to_ignore or callable(filter) and not filter(key):
            continue
        setattr(obj, key, value)


def fill_form_data_with_engagement(form: FlaskForm, host: Host):
    for key, value in host.__dict__.items():
        if not key.startswith('engagement_'):
            continue
        field = getattr(form, key, None)
        if not field:
            continue
        field.data = value


def engagement_fields(key: str):
    return key.startswith('engagement_')


def ignore_if_audit(key: str):
    engagement = engagement_fields(key)
    return not engagement or current_user.view != 'inboxPlacementAudit'


class HasHostSelectFieldForm(FlaskForm):
    host = SelectField('Choose a host')

    def populate_hosts(self, hosts: list[Host]):
        self.host.choices = [(host.id, host.name) for host in hosts]


class HasTimezoneSelectForm(FlaskForm):
    timezone = SelectField('Timezone')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__populate_timezones()

    def __populate_timezones(self):
        timezones = parsed_timezones()
        self.timezone.choices = [
            (
                timezone['name'],
                f'{timezone["name"]} ({timezone["parsed_offset"]})',
            )
            for timezone in timezones
        ]
