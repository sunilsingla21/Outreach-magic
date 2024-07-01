from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms.validators import InputRequired

from app.proxy_details.validators import ValidProxyString


class ProxyDetailsForm(FlaskForm):
    proxies = TextAreaField(
        'Proxy Strings (separated by newline)',
        validators=[
            InputRequired(),
            ValidProxyString(),
        ]
    )
