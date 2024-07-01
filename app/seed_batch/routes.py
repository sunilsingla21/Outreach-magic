from datetime import datetime

import requests
from bson import ObjectId
from flask import abort, flash, redirect, request, url_for
from flask_login import current_user, login_required

from app.extensions import secret_manager
from app.models import *
from app.seed_batch import bp
from app.seed_batch.forms import (PlacementAuditSeedBatchForm, SeedBatchForm,
                                  form_with_esp_fields)
from app.utils.forms import (engagement_fields, get_form_error_string,
                             ignore_if_audit, update_data_from_form)


@bp.post('/add')
@login_required
def add():
    from wtforms.validators import NumberRange

    esps = Account.get_count_per_esp(
        request.form.get('generate_type', 'engagement'))
    if current_user.view == 'inboxPlacementAudit':
        base_form = PlacementAuditSeedBatchForm
    else:
        base_form = SeedBatchForm
    form = form_with_esp_fields(esps, base_form)()
    extra_validators = {
        f'esp_{esp}': [NumberRange(0, count)]
        for esp, count in esps.items()
    }
    form.populate_hosts(current_user.hosts)

    response = redirect(url_for('user.seeds'))
    if not form.validate_on_submit(extra_validators):
        for key in form.errors:
            flash(get_form_error_string(key, form.errors), category='error')
        return response

    host_id = ObjectId(form.host.data)
    host = Host.get_by_id(host_id)
    if not host or host_id not in current_user.host_ids:
        abort(401)

    seed_batch = SeedBatch(
        status='ready',
        host_id=host_id,
        date_added=datetime.utcnow(),
    )

    update_data_from_form(
        seed_batch,
        form,
        keys_to_ignore=['host', 'sender_addresses'],
        filter=ignore_if_audit,
    )

    seed_batch.save()
    if current_user.view != 'inboxPlacementAudit':
        update_data_from_form(host, form, filter=engagement_fields)

    host.external_sender_addresses = form.sender_addresses.data
    host.save()

    flash('Seed batch generated successfully')

    function_url = secret_manager.get('SEED_EMAILS_GENERATOR_URL')
    requests.post(function_url)
    return response


@bp.get('/<string:id>')
@login_required
def download(id):
    seed_batch = SeedBatch.get_by_id(id)
    if not seed_batch:
        abort(404)
    if seed_batch.host_id not in current_user.host_ids:
        abort(401)
    if seed_batch.status == 'expired':
        abort(410)

    response = requests.head(seed_batch.csv_url)
    if response.status_code >= 400:
        seed_batch.status = 'expired'
        seed_batch.save()
        abort(410)

    return redirect(seed_batch.csv_url)
