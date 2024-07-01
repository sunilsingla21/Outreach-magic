from functools import wraps

from flask import abort, flash, g, session
from flask_login import current_user

from app.account.forms import NewAccountForm
from app.models import Host
from app.utils.forms import get_form_error_string


def validate_host_form(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        form = NewAccountForm()
        form.populate_hosts(current_user.hosts)
        if not form.validate_on_submit():
            for key in form.errors:
                flash(get_form_error_string(key, form.errors), category='error')
            abort(400)

        host_id = form.host.data
        host = Host.get_by_id(host_id)
        if not host:
            flash('Invalid host')
            abort(400)

        if host.id not in current_user.host_ids:
            abort(401)
        g.host = host
        session['host'] = str(host.id)
        return f(*args, **kwargs)
    return decorated_function


def validate_host_session(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'host' not in session:
            flash('No host provided', category='error')
            abort(400)

        host: Host = Host.get_by_id(session['host'])
        if not host:
            flash('Invalid host', category='error')
            abort(400)

        if host.id not in current_user.host_ids:
            flash('Unauthorized')
            abort(401)
        g.host = host
        return f(*args, **kwargs)
    return decorated_function
