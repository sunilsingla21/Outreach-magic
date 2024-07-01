from flask import flash
from wtforms import TextAreaField, ValidationError

from app.models import ProxyDetails


class ValidProxyString:
    def __init__(self, message=None):
        if not message:
            message = "Field must contain valid proxy strings (address:port:username:password)"
        self.message = message

    def __call__(self, _, field: TextAreaField):
        for index, line in enumerate(field.data.splitlines(), 1):
            splitted_data = line.split(':')
            if len(splitted_data) != 4:
                raise ValidationError(self.message)
            try:
                splitted_data[1] = int(splitted_data[1])
            except ValueError:
                raise ValidationError(
                    f'Invalid port on line {index} ({splitted_data[1]})')


class NonExistingProxyDetails:

    def __call__(self, _, field: TextAreaField):
        data = []
        for line in field.data.splitlines():
            count = ProxyDetails.count(
                {ProxyDetails._mongo_map['string']: line}
            )
            if count > 0:
                flash(f'Proxy details already exist: {line}', category='info')
            else:
                data.append(line)
        field.data = data
