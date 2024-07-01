from flask_wtf import FlaskForm
from wtforms import (BooleanField, EmailField, HiddenField, RadioField,
                     SelectField, StringField, SubmitField, TextAreaField)
from wtforms.validators import InputRequired

from app.account.validators import ValidBulkAccounts
from app.models import VPS
from app.utils.forms import HasHostSelectFieldForm
from app.utils.validators import EMAIL_REGEX, LineSeparatedValues, Strip

ENGAGE_VIA_CHOICES = [
    ('api', 'API'),
]

STATUS_CHOICES = [('active', 'Active'), ('disabled', 'Disabled')]


class EditAccountForm(FlaskForm):
    status = SelectField(
        'Status',
        choices=STATUS_CHOICES,
    )
    inbox_placement_active = BooleanField('Inbox Placement')
    inbox_engagement_active = BooleanField('Inbox Engagement')


class AdminEditAccountForm(EditAccountForm):
    placement_account_active = BooleanField('Placement Account')
    engagement_account_active = BooleanField('Engagement Account')
    engagement_via = RadioField(
        'Engage via',
        choices=ENGAGE_VIA_CHOICES,
        validators=[InputRequired()]
    )
    inbox_reset = BooleanField('Inbox Reset (activate on next run)')
    password = StringField('Update Password')
    two_fa = StringField('Update 2FA Key')
    relay_account = BooleanField('Relay Account')
    vps = SelectField('VPS')

    def populate_vps(self, machines: list[VPS]):
        self.vps.choices = [
            (None, 'None'),
            *[
                (vps.machine_id, vps.name)
                for vps in machines
            ]
        ]


class AddAccountAppPasswordForm(FlaskForm):
    host_id = HiddenField(validators=[InputRequired()])
    server = HiddenField(validators=[InputRequired()])
    sender_name = StringField(
        'Your name',
        validators=[InputRequired()],
    )
    username = EmailField(
        'Email',
        validators=[InputRequired(), Strip()],
    )
    app_password = StringField(
        'App Password',
        validators=[InputRequired()],
    )


class BulkAppPasswordForm(HasHostSelectFieldForm):
    regex = EMAIL_REGEX + r':.+:.+:.+'
    accounts = TextAreaField(
        'Accounts separated by new lines (username:password:name:server)',
        validators=[
            LineSeparatedValues(
                regex,
                message='Lines do not follow the correct format',
                ignore_lines_with_errors=True,
            ),
            ValidBulkAccounts(),
        ],
    )
    status = SelectField(
        'Status',
        choices=[('active', 'Active'), ('disabled', 'Disabled')],
    )
    placement_account_active = BooleanField('Placement Account')
    engagement_account_active = BooleanField('Engagement Account')
    engagement_via = RadioField(
        'Engage via',
        choices=ENGAGE_VIA_CHOICES,
        validators=[InputRequired()]
    )


class NewAccountForm(HasHostSelectFieldForm):
    add_google = SubmitField('Google account')
    add_microsoft = SubmitField('Microsoft account')
    add_yahoo = SubmitField('Yahoo account')
