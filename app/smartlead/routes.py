import os
from datetime import datetime

import requests
from bson import ObjectId
from flask import abort, flash, redirect, url_for
from flask_login import current_user, login_required
from pymongo import UpdateOne

from app.extensions import mongo
from app.models import Host, SmartleadAccount
from app.smartlead import bp
from app.smartlead.forms import EditSmartleadAccountForm, UpdateAccountsForm
from app.utils.accounts import calculate_esp
from app.utils.forms import get_form_error_string

ACCOUNT_TYPES_MAP = {
    'GMAIL': 'google',
    'OUTLOOK': 'microsoft',
}


def _process_accounts(host: Host, bulk_updates: list, offset: int, limit=100):
    api_base_url = os.getenv('SMARTLEAD_API_BASE_URL')
    response = requests.get(api_base_url +
                            f'?api_key={host.smartlead_api_key}&offset={offset}&limit={limit}')
    response.raise_for_status()
    data = response.json()
    for account in data:
        server = ACCOUNT_TYPES_MAP[account['type']]
        esp, esp_camel_case = calculate_esp(account['username'], server)
        root_data = {
            'username': account['username'],
            'hostId': host.id,
            'hostName': host.name,
            'server': server,
            'esp': esp,
            'espCamelCase': esp_camel_case,
            'lastUpdated': datetime.utcnow(),
        }
        bulk_updates.append(UpdateOne(
            filter={'username': account['username']},
            update={
                '$setOnInsert': root_data,
                '$set': {
                    'smartlead': account
                },
            },
            upsert=True,
        ))

    return offset + limit if len(data) == limit else None


@bp.post('/update-accounts')
@login_required
def update_accounts():
    response = redirect(url_for('user.smartlead', page=1))
    hosts_with_api_key = [h for h in current_user.hosts if h.smartlead_api_key]
    form = UpdateAccountsForm()
    form.populate_hosts(hosts_with_api_key)
    if not form.validate_on_submit():
        for key in form.errors:
            flash(get_form_error_string(key, form.errors), category='error')
        return response

    host = Host.get_by_id(form.host.data)
    if not host:
        abort(404)
    if host.id not in current_user.host_ids:
        abort(401)
    if not host.smartlead_api_key:
        abort(400)

    bulk_updates = []
    offset = 0
    while offset is not None:
        offset = _process_accounts(host, bulk_updates, offset)

    if bulk_updates:
        results = mongo.smartleadEmailAccounts.bulk_write(bulk_updates)
        flash(
            f'{results.upserted_count} new accounts added. {results.modified_count} accounts updated.')
    else:
        flash('No new accounts found', category='info')
    return response


@bp.post('/account/<string:id>')
@login_required
def edit_account(id):
    response = redirect(url_for('user.smartlead', page=1))
    account = SmartleadAccount.get_by_id(id)
    if not account:
        abort(404)
    if account.host_id not in current_user.host_ids:
        abort(401)

    form = EditSmartleadAccountForm()
    form.populate_hosts(current_user.hosts)
    if not form.validate_on_submit():
        for key in form.errors:
            flash(get_form_error_string(key, form.errors), category='error')
        return response

    account.host_id = ObjectId(form.host.data)
    account.host_name = current_user.host_map[account.host_id].name
    account.esp = form.esp.data
    account.save()
    flash('Account updated successfully')
    return response
