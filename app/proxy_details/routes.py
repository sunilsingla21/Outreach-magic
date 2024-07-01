from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from wtforms.widgets import TextInput

from app.models import *
from app.proxy_details import bp
from app.proxy_details.forms import ProxyDetailsForm
from app.proxy_details.validators import NonExistingProxyDetails
from app.utils.forms import get_form_error_string


@bp.post('/add')
@login_required
def add():
    if current_user.view != 'admin':
        abort(403)
    form = ProxyDetailsForm()
    response = redirect(url_for('user.email_groups'))
    if not form.validate_on_submit({'proxies': [NonExistingProxyDetails()]}):
        for key in form.errors:
            flash(get_form_error_string(key, form.errors), category='error')
        return response

    for line in form.proxies.data:
        ProxyDetails.from_string(line).save()

    if form.proxies.data:
        flash('New proxy details created successfully')
    return response


@bp.route('/<string:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    if current_user.view != 'admin':
        abort(403)
    proxy = ProxyDetails.get_by_id(id)
    if not proxy:
        abort(404)
    form = ProxyDetailsForm()
    form.proxies.widget = TextInput()
    form.proxies.label.text = 'Proxy string'
    if request.method == 'GET':
        form.proxies.data = proxy.string
        return render_template('user/edit_proxy.html.j2', proxy=proxy, form=form)

    response = redirect(url_for('proxy_details.edit', id=id))
    if not form.validate_on_submit():
        for key in form.errors:
            flash(get_form_error_string(key, form.errors), category='error')
        return response
    if len(form.proxies.data) == 0:
        return response

    new_proxy = ProxyDetails.from_string(form.proxies.data)
    new_proxy.id = proxy.id
    new_proxy.save()
    flash('Proxy updated successfully')
    return response


@bp.delete('/<string:id>')
@login_required
def delete(id):
    if current_user.view != 'admin':
        abort(403)
    proxy = ProxyDetails.get_by_id(id)
    if not proxy:
        abort(404)
    proxy.delete()
    flash('Proxy deleted successfully', category='info')
    return redirect(url_for('user.email_groups'))


@bp.get('/<string:id>')
@login_required
def get(id):
    if current_user.view != 'admin':
        abort(403)
    proxy_details = ProxyDetails.get_by_id(id)
    if not proxy_details:
        abort(404)
    return {
        'ip': proxy_details.ip,
        'port': proxy_details.port,
        'username': proxy_details.username,
        'password': proxy_details.password,
        'string': proxy_details.string,
    }
