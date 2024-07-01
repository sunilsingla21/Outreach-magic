from wtforms import BooleanField, FileField, SelectField, StringField
from wtforms.validators import InputRequired

from app.csv_upload.validators import FileExtension, ValidCSVUpload
from app.utils.forms import HasHostSelectFieldForm


class NewCSVUploadForm(HasHostSelectFieldForm):
    import_source = SelectField(
        'Sourced from',
        choices=[
            ('apollo', 'Apollo'),
            ('growmeorganic_linkedin', 'GrowMeOrganic (Linkedin)'),
        ],
    )
    import_name = StringField(
        'How would you describe this upload?',
        validators=[InputRequired()],
    )
    csv_file = FileField(
        'Upload the CSV file',
        validators=[InputRequired(), FileExtension(['csv']), ValidCSVUpload()],
    )
    update_existing = BooleanField(
        'Replace attributes on records with existing import name',
    )
