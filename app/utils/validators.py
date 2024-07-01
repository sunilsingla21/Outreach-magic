import re

from flask import flash
from wtforms import TextAreaField, ValidationError

EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
DOMAIN_REGEX = r'^((?!-))(xn--)?[a-z0-9][a-z0-9-_]{0,61}[a-z0-9]{0,1}\.(xn--)?([a-z0-9\-]{1,61}|[a-z0-9-]{1,30}\.[a-z]{2,})$'
email_regex = re.compile(f'(^{EMAIL_REGEX}$)')


class Strip():
    def __call__(self, form, field):
        field.data = field.data.strip()


class LineSeparatedValues(object):
    def __init__(self, regex, message=None, ignore_lines_with_errors=False):
        if not message:
            message = "Field must contain valid line separated values"
        self.ignore_lines_with_errors = ignore_lines_with_errors
        self.regex = re.compile(regex)
        self.message = message

    def __call__(self, form, field: TextAreaField):
        lines = [
            e
            for email in field.data.splitlines()
            if (e := email.strip())
        ]

        filtered_lines = []
        for index, line in enumerate(lines, 1):
            if self.regex.match(line):
                filtered_lines.append(line)
                continue
            if self.ignore_lines_with_errors:
                flash(
                    f'Line #{index} did not follow the correct format', category='error')
            else:
                raise ValidationError(self.message)

        field.data = filtered_lines
