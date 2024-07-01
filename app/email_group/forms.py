from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField

from app.account.forms import STATUS_CHOICES


class UpdateGroupForm(FlaskForm):
    status = SelectField(
        'Status',
        choices=STATUS_CHOICES,
    )
    placement_account_active = BooleanField('Placement Account')
    engagement_account_active = BooleanField('Engagement Account')
