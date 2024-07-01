from flask import abort, flash, redirect, url_for
from flask_login import current_user, login_required

from app.models import *
from app.utils.forms import get_form_error_string
from app.vps import bp
from app.vps.forms import VPSForm


@bp.post('')
@login_required
def create():
    if not current_user.view == 'admin':
        abort(403)

    response = redirect(url_for('user.vps'))
    form = VPSForm()
    if not form.validate_on_submit():
        for key in form.errors:
            flash(get_form_error_string(key, form.errors), category='error')
        return response

    vps = VPS(
        name=form.name.data,
        status=form.status.data,
        machine_id=form.machine_id.data,
        hardware=form.hardware.data,
        provider=form.provider.data,
    )
    vps.save()
    return response


@bp.post('/account/<string:id>')
@login_required
def edit(id):
    if not current_user.view == 'admin':
        abort(403)

    response = redirect(url_for('user.vps'))
    vps = VPS.get_by_id(id)
    if not vps:
        abort(404)

    form = VPSForm()
    if not form.validate_on_submit():
        for key in form.errors:
            flash(get_form_error_string(key, form.errors), category='error')
        return response

    vps.name = form.name.data
    vps.status = form.status.data
    vps.machine_id = form.machine_id.data
    vps.hardware = form.hardware.data
    vps.provider = form.provider.data
    vps.save()
    flash('VPS updated successfully')
    return response
