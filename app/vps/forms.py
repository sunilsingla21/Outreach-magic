from flask_wtf import FlaskForm
from wtforms import SelectField, StringField
from wtforms.validators import InputRequired


class VPSForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    status = SelectField('Status', choices=[
        ('ready', 'Ready'),
        ('disabled', 'Disabled'),
    ])
    machine_id = StringField('ID', validators=[InputRequired()])
    hardware = StringField('Hardware', validators=[InputRequired()])
    provider = StringField('Provider')
