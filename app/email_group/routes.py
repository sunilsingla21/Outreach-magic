from bson import ObjectId
from flask import abort, flash, redirect, url_for
from flask_login import current_user, login_required

from app.email_group import bp
from app.email_group.forms import UpdateGroupForm
from app.models import *
from app.utils.forms import get_form_error_string


@bp.post('/<string:id>')
@login_required
def update(id):
    if current_user.view != 'admin':
        abort(403)

    group = EmailGroup.get_by_id(id)
    if not group:
        abort(404)

    response = redirect(url_for('user.email_groups'))
    form = UpdateGroupForm()
    if not form.validate_on_submit():
        for key in form.errors:
            flash(get_form_error_string(key, form.errors))
        return response

    update = {
        '$set': {
            Account._mongo_map[field.name]: field.data
            for field in form if field.name != 'csrf_token'
        }
    }
    result = Account.update_many(
        filter={Account._mongo_map['email_group_id']: group.id},
        update=update,
    )
    flash(
        f'{result.modified_count} accounts were updated',
        category='message' if result.modified_count > 0 else 'info',
    )
    return response


@bp.post('/<string:id>/reset')
@login_required
def reset(id):
    if current_user.view != 'admin':
        abort(403)

    if id == 'all':
        condition = {'$ne': None}
    else:
        group = EmailGroup.get_by_id(id)
        if not group:
            abort(404)
        condition = group.id

    result = Account.update_many(
        filter={Account._mongo_map['email_group_id']: condition},
        update={'$unset': {Account._mongo_map['email_group_id']: ''}},
    )
    if id != 'all':
        group.calculate_server_counts()
        group.save()
    else:
        EmailGroup.update_many(
            filter={},
            update={'$unset': {'counts': ''}},
        )
    EmailGroup.invalidate_caches()
    flash(f'{result.modified_count} accounts were reset', category='info')
    return redirect(url_for('user.email_groups'))


@bp.post('/assign-unassigned')
@login_required
def assign_unassigned():
    if current_user.view != 'admin':
        abort(403)
    accounts_assigned = EmailGroup.assign_unassigned()

    EmailGroup.invalidate_caches()
    flash(
        f'{accounts_assigned} accounts were assigned',
        category='message' if accounts_assigned > 0 else 'info',
    )
    return redirect(url_for('user.email_groups'))
