import csv

from wtforms import FileField
from wtforms.validators import ValidationError


class FileExtension:
    def __init__(self, extensions: list[str], message=None):
        self.extensions = extensions
        if not message:
            message = f'Invalid file type. Allowed extensions are {", ".join([f".{ext}" for ext in extensions])}'
        self.message = message

    def __call__(self, form, field: FileField):
        if not field.data:
            return
        filename: str = field.data.filename
        extension = filename.split('.')[-1]
        if extension not in self.extensions:
            raise ValidationError(self.message)


class ValidCSVUpload:
    def __get_csv_reader(self, file):
        try:
            csv_text: list[str] = file.read().decode('utf-8').splitlines()
            file.seek(0)
            self.reader = csv.DictReader(csv_text)
        except Exception:
            raise ValidationError('Not a CSV text file')

    def __validate_apollo(self):
        apollo_headers = set(['Email', 'Apollo Contact Id'])
        if not self.__main_headers.issuperset(apollo_headers):
            raise ValidationError(self.message)

    def __validate_growmeorganic_linkedin(self):
        growmeorganic_headers = set(
            ['email_first', 'first_name', 'job_title', 'company_name',]
        )
        if not self.__main_headers.issuperset(growmeorganic_headers):
            raise ValidationError(self.message)

    def __call__(self, form, field: FileField):
        self.__get_csv_reader(field.data)
        self.__main_headers = set(self.reader.fieldnames)
        if form.import_source.data == 'apollo':
            self.message = 'Cannot find fields "Email" and/or "Apollo Contact Id" in the header row. Are you sure this is an Apollo CSV upload?'
            self.__validate_apollo()
        elif form.import_source.data == 'growmeorganic_linkedin':
            self.message = 'The file does not have the correct format. Are you sure this is a GrowMeOrganic (Linkedin) CSV upload?'
            self.__validate_growmeorganic_linkedin()
