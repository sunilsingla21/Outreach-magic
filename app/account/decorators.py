from functools import wraps

from flask import abort, g
from flask_login import current_user

from app.models import Account


def validate_account(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        account_id = kwargs.get('id', None)
        account = Account.get_by_id(account_id)
        if not account:
            abort(404)
        if account.host_id not in current_user.host_ids:
            abort(401)
        g.account = account
        return f(*args, **kwargs)
    return decorated_function
