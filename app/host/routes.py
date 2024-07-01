from bson import ObjectId
from flask import (Response, abort, flash, redirect, render_template, request,
                   url_for)
from flask_login import current_user, login_required

from app.host import bp
from app.host.forms import (AddExistingHostForm, HostForm,
                            PlacementAuditHostForm)
from app.models import *
from app.utils.forms import (get_form_error_string, ignore_if_audit,
                             update_data_from_form)


@bp.post('')
@login_required
def create():
    response = redirect(url_for('user.hosts'))

    if current_user.view == 'inboxPlacementAudit':
        form = PlacementAuditHostForm()
    else:
        form = HostForm()
    if not form.validate_on_submit():
        for key in form.errors:
            flash(get_form_error_string(key, form.errors), category='error')
        return response

    name = form.name.data
    if Host.get_by_name(name):
        flash('Host already exists', category='error')
        return response

    host = Host()
    update_data_from_form(host, form, filter=ignore_if_audit)
    host.save()
    current_user.host_ids.append(host.id)
    current_user.save()
    flash('Host created successfully')
    return response


@bp.post('/add')
@login_required
def add():
    response = redirect(url_for('user.hosts'))

    form = AddExistingHostForm()
    if not form.validate_on_submit():
        for key in form.errors:
            flash(get_form_error_string(key, form.errors), category='error')
        return response

    host_crypt = form.host_crypt.data
    host = Host.get_by_crypt(host_crypt)
    if host:
        if host.id in current_user.host_ids:
            flash('Host is already added', category='info')
            return response

        current_user.host_ids.append(host.id)
        current_user.save()
        flash('Added host successfully')
        return response

    flash('Host crypt is not found. Check if you typed it in correctly. If not, try adding a new host',
          category='error')
    return response


@bp.post('/<string:id>')
@login_required
def edit(id):
    host = Host.get_by_id(id)
    if not host:
        abort(404)
    if host.id not in current_user.host_ids:
        abort(401)

    response = redirect(request.args.get('next') or url_for('user.hosts'))
    if current_user.view == 'inboxPlacementAudit':
        form = PlacementAuditHostForm()
    else:
        form = HostForm()
    if not form.validate_on_submit():
        for key in form.errors:
            flash(get_form_error_string(key, form.errors), category='error')
        return response

    update_data_from_form(host, form, ['name'], filter=ignore_if_audit)
    host.save()
    flash('Host updated successfully')
    return response


@bp.delete('/<string:id>')
@login_required
def delete(id):
    try:
        current_user.host_ids.remove(ObjectId(id))
        current_user.save()
        flash('Host deleted successfully')
    except ValueError:
        flash('Host does not exist', category='error')
        return abort(404)
    return Response(status=204)


@bp.get('/<string:id>/engagement-settings')
@login_required
def engagement_settings(id):
    host = Host.get_by_id(id)
    if not host:
        abort(404)
    if host.id not in current_user.host_ids:
        abort(401)
    return {
        key: value
        for key, value in host.__dict__.items() if key.startswith('engagement_')
    }


@bp.get('/<string:name>')
@login_required
def details(name: str):
    host = Host.get_by_name(name)
    def engagement_fields(field): return 'engagement' in field.name

    if not host:
        abort(404)
    if host.id not in current_user.host_ids:
        abort(401)

    if current_user.view == 'inboxPlacementAudit':
        form = PlacementAuditHostForm()
    else:
        form = HostForm()
    form.prepare_for_host(host)

    return render_template('host/details.html.j2', host=host, form=form, engagement_fields=engagement_fields)


@bp.get('/<string:name>/dashboard')
@login_required
def dashboard(name: str):
    host = Host.get_by_name(name)
    if not host:
        abort(404)
    if host.id not in current_user.host_ids:
        abort(401)

    return render_template(
        'dashboard.html.j2',
        title=f'Dashboard for {host.name}',
        iframe_url=host.looker_studio_url,
    )
