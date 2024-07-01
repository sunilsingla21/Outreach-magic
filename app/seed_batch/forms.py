from wtforms import IntegerField, SelectField, StringField, TextAreaField
from wtforms.validators import InputRequired, NumberRange

from app.host.forms import DisabledEngagementFields, EngagementFields, HostForm
from app.models import Host
from app.utils.forms import (HasHostSelectFieldForm,
                             fill_form_data_with_engagement)


class SeedBatchForm(EngagementFields, HasHostSelectFieldForm):
    name = StringField(
        'Give this list a name',
        validators=[InputRequired()],
    )
    generate_type = SelectField(
        'Type of account',
        choices=[('engagement', 'Engagement'), ('placement', 'Placement')],
        default='engagement',
    )
    sender_addresses = TextAreaField(
        'Sender addresses (separated by newlines)',
        validators=HostForm.external_sender_addresses_validators,
    )

    def populate_hosts(self, hosts: list[Host]):
        super().populate_hosts(hosts)
        if len(hosts) == 0:
            return

        if self.is_submitted():
            return

        first_host = hosts[0]
        fill_form_data_with_engagement(self, first_host)
        self.sender_addresses.data = '\n'.join(
            first_host.external_sender_addresses)


class PlacementAuditSeedBatchForm(DisabledEngagementFields, SeedBatchForm):
    pass


def form_with_esp_fields(esp_data: dict[str, int], Form):
    attrs = dict(Form.__dict__)
    attrs.update({
        f'esp_{esp}': IntegerField(
            f'{esp} - ({count})',
            default=0,
            validators=[InputRequired(), NumberRange(min=0, max=count)],
        )
        for esp, count in esp_data.items()
    })

    return type('DynamicForm', (Form,), attrs)
