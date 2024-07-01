from pymongo.collection import Collection
from wtforms import StringField, TextAreaField
from wtforms.validators import ValidationError

from app.utils.validators import email_regex


class CommaSeparatedEmails(object):
    def __init__(self, message=None):
        if not message:
            message = "Field must contain valid comma-separated email addresses."
        self.message = message

    def __call__(self, form, field: StringField):
        emails = [
            stripped for email in field.data.split(',')
            if (stripped := email.strip())
        ]

        for email in emails:
            if not email_regex.match(email):
                raise ValidationError(self.message)


class NotExistingEmail(object):
    def __init__(self, collection: Collection, message=None):
        if not message:
            message = 'Email addresses cannot exist in the database'
        self.collection = collection
        self.message = message

    def __call__(self, form, field: TextAreaField):
        if type(field.data) is not list:
            return

        count = self.collection.count_documents({
            'username': {'$in': field.data}
        })
        if count > 0:
            raise ValidationError(self.message)
