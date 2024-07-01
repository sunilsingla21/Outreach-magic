from wtforms import SelectField

from app.utils.forms import HasHostSelectFieldForm


class UpdateAccountsForm(HasHostSelectFieldForm):
    pass


class EditSmartleadAccountForm(HasHostSelectFieldForm):
    esp = SelectField(
        'OM ESP',
        choices=[
            ('google business', 'google business'),
            ('google personal', 'google personal'),
            ('microsoft personal', 'microsoft personal'),
            ('microsoft business', 'microsoft business'),
        ],
    )
