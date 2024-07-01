import os
from datetime import datetime

import requests
from flask import Response, abort, flash, g, redirect, session, url_for
from flask_login import current_user, login_required

from app.account import bp
from app.account.decorators import validate_account
from app.account.forms import (AddAccountAppPasswordForm, AdminEditAccountForm,
                               BulkAppPasswordForm, EditAccountForm)
from app.extensions import secret_manager
from app.models import *
from app.utils.forms import get_form_error_string, update_data_from_form


@bp.post('/add')
@login_required
def add():
    form = AddAccountAppPasswordForm()
    if not form.validate_on_submit():
        return {
            'message': '\n'.join([
                get_form_error_string(key, form.errors)
                for key in form.errors
            ])
        }, 400

    host = Host.get_by_id(form.host_id.data)
    if not host or host.id not in current_user.host_ids:
        return {'message': 'Invalid host information'}, 401

    username = form.username.data
    existing_account = Account.get_by_email(username)
    if existing_account:
        return {'message': 'Account already exists'}, 401

    account = Account(
        host_id=host.id,
        server=form.server.data,
        status='active',
        connection_type='App Password',
        time_added=datetime.utcnow(),
    )
    update_data_from_form(account, form, ['host_id'])
    account.save()
    if account.server == 'google':
        session['google_success'] = True
    else:
        flash('Account added successfully')
    return {}, 201


@bp.post('/bulk-add')
@login_required
def bulk_add():
    form = BulkAppPasswordForm()
    form.populate_hosts(current_user.hosts)
    if not form.validate_on_submit():
        for key in form.errors:
            flash(get_form_error_string(key, form.errors), category='error')
            abort(400)

    host = Host.get_by_id(form.host.data)
    if not host or host.id not in current_user.host_ids:
        abort(401)
    for account in form.accounts.data:
        account.save()
    if form.accounts.data:
        flash(f'{len(form.accounts.data)} accounts saved successfully')
    return redirect(url_for('user.emails'))


@bp.get('/seed-account-counts/<string:account_type>')
@login_required
def seed_accounts_count(account_type: str):
    return Account.get_count_per_esp(account_type)


@bp.post('/<string:id>/edit')
@login_required
@validate_account
def edit(id):
    account: Account = g.account

    response = redirect(url_for('user.emails'))
    if current_user.view == 'admin':
        form = AdminEditAccountForm()
        form.populate_vps(VPS.get_all())
    else:
        form = EditAccountForm()
    if not form.validate_on_submit():
        for key in form.errors:
            flash(get_form_error_string(key, form.errors), category='error')
        return response

    update_data_from_form(account, form, ['vps', 'password', 'two_fa'])
    if current_user.view == 'admin':
        if form.vps.data == 'None':
            account.machine_id = None
            account.vps_name = None
        else:
            account.machine_id = form.vps.data
            vps = VPS.get({'id': account.machine_id})
            if not vps:
                abort(400)
            account.vps_name = vps.name
        if form.password.data:
            secret_manager.create_secret_version(
                f'{account.id}_PASSWORD',
                form.password.data,
                os.getenv('GOOGLE_PASSWORDS_PROJECT'),
            )
            account.last_updated_password = datetime.utcnow()
        if form.two_fa.data:
            secret_manager.create_secret_version(
                f'{account.id}_2FA_KEY',
                form.two_fa.data.replace(' ', ''),
                os.getenv('GOOGLE_PASSWORDS_PROJECT'),
            )
            account.last_updated_2fa = datetime.utcnow()

    account.save()
    flash('Account updated successfully')
    return response


@bp.post('/<string:id>/test')
@login_required
@validate_account
def test(id):
    account: Account = g.account
    test_account_url = secret_manager.get('TEST_ACCOUNT_URL')

    response = requests.post(f'{test_account_url}&id={account.id}')
    response.raise_for_status()

    data = response.json()
    account.smtp_result = data['smtp']
    account.imap_result = data['imap']
    account.tests_last_updated = datetime.utcnow()
    account.save()

    return data, 200


@bp.delete('/<string:id>')
@login_required
@validate_account
def delete(id):
    account: Account = g.account
    account.delete()
    flash('Account deleted successfully')
    return Response(status=204)
