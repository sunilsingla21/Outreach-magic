from flask import g, render_template
from flask_login import login_required

from app.account.forms import AddAccountAppPasswordForm
from app.decorators.accounts import validate_host_form
from app.models import *
from app.yahoo import bp


@bp.post('/add')
@login_required
@validate_host_form
def add():
    host: Host = g.host
    form = AddAccountAppPasswordForm()
    form.host_id.data = str(host.id)
    form.server.data = 'yahoo'
    return render_template('yahoo/add.html.j2', form=form)
