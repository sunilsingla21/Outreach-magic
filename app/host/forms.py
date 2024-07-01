from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length, Regexp

from app.extensions import mongo
from app.host.validators import CommaSeparatedEmails, NotExistingEmail
from app.models import Host
from app.utils.forms import (HasTimezoneSelectForm,
                             fill_form_data_with_engagement)
from app.utils.validators import EMAIL_REGEX, LineSeparatedValues


class EngagementFields(FlaskForm):
    engagement_remove_spam = BooleanField('Remove Spam', default=False)
    engagement_mark_important = BooleanField('Mark important', default=False)
    engagement_reply_message = BooleanField('Reply message', default=False)
    engagement_move_primary = BooleanField('Move to primary', default=False)
    engagement_click_link = BooleanField('Click link', default=False)
    engagement_download_message = BooleanField(
        'Download message', default=False)
    engagement_scroll_message = BooleanField('Scroll message', default=False)


def _generate_disabled_engagement_fields():
    attrs = dict(EngagementFields.__dict__)
    for key, field in attrs.items():
        if 'engagement' not in key:
            continue
        new_kwargs = {
            **field.kwargs,
            'render_kw': {
                'disabled': True,
                'title': "You don't have permission to update this setting",
            },
        }
        attrs[key] = BooleanField(*field.args, **new_kwargs)
    return type('EngagementFieldsDisabled', (EngagementFields,), attrs)


DisabledEngagementFields = _generate_disabled_engagement_fields()


class HostForm(EngagementFields, HasTimezoneSelectForm):
    external_sender_addresses_validators = [
        LineSeparatedValues(EMAIL_REGEX),
        NotExistingEmail(mongo.emailAccounts),
        NotExistingEmail(mongo.smartleadEmailAccounts),
    ]
    name = StringField(
        'Host name',
        validators=[
            InputRequired(),
            Length(min=3, max=20),
            Regexp(
                r'^\w[\w.-_]+\w$', message='has to start and end with a letter, and can only contain these symbols: . - _'),
        ])
    smartlead_api_key = StringField(
        'Smartlead API Key',
        validators=[]
    )
    external_sender_addresses = TextAreaField(
        'External sender addresses (separated by newlines)',
        validators=external_sender_addresses_validators,
    )
    notification_address_string = StringField(
        'Notification addresses (separated by comma)',
        validators=[CommaSeparatedEmails()],
    )

    def prepare_for_host(self, host: Host):
        self.timezone.data = host.timezone
        self.external_sender_addresses.data = '\n'.join(
            host.external_sender_addresses)
        self.notification_address_string.data = host.notification_address_string.strip()
        fill_form_data_with_engagement(self, host)


class PlacementAuditHostForm(DisabledEngagementFields, HostForm):
    pass


class AddExistingHostForm(FlaskForm):
    host_crypt = StringField(
        'Host crypt',
        validators=[
            InputRequired(),
        ])
    submit = SubmitField('Add')
