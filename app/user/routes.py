from datetime import datetime
from functools import wraps
from threading import Thread

import requests
from flask import abort, render_template
from flask_login import current_user, login_required
from wtforms import Field

from app.account.forms import (AdminEditAccountForm, BulkAppPasswordForm,
                               EditAccountForm, NewAccountForm)
from app.csv_upload.forms import NewCSVUploadForm
from app.email_group.forms import UpdateGroupForm
from app.extensions import mongo, secret_manager
from app.host.forms import (AddExistingHostForm, HostForm,
                            PlacementAuditHostForm)
from app.models import *
from app.proxy_details.forms import ProxyDetailsForm
from app.seed_batch.forms import (PlacementAuditSeedBatchForm, SeedBatchForm,
                                  form_with_esp_fields)
from app.smartlead.forms import EditSmartleadAccountForm, UpdateAccountsForm
from app.user import bp
from app.vps.forms import VPSForm


@bp.get('')
@login_required
def index():
    return render_template('user/index.html.j2')


def validate_view(f):
    """
    Abort if the current user's view can't access the page
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from app.utils.constants import PAGES_FOR_VIEW
        if f.__name__ not in PAGES_FOR_VIEW[current_user.view]:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@bp.get('/hosts')
@login_required
@validate_view
def hosts():
    def engagement_fields(field): return 'engagement' in field.name

    if current_user.view == 'inboxPlacementAudit':
        new_host_form = PlacementAuditHostForm()
    else:
        new_host_form = HostForm()

    add_existing_host_form = AddExistingHostForm()
    return render_template(
        'user/hosts.html.j2',
        new_host_form=new_host_form,
        add_existing_host_form=add_existing_host_form,
        engagement_fields=engagement_fields,
    )


@bp.get('/smartlead/<int:page>')
@login_required
@validate_view
def smartlead(page):
    if page <= 0:
        abort(400)
    user: User = current_user
    limit = 15
    accounts = user.get_smartlead_accounts(limit + 1, (page - 1) * limit)
    has_next_page = len(accounts) > limit
    if has_next_page:
        accounts = accounts[:-1]

    hosts_with_api_key = [h for h in current_user.hosts if h.smartlead_api_key]

    form = EditSmartleadAccountForm()
    form.populate_hosts(current_user.hosts)

    update_accounts_form = UpdateAccountsForm()
    update_accounts_form.populate_hosts(hosts_with_api_key)

    return render_template(
        'user/smartlead.html.j2',
        form=form,
        update_accounts_form=update_accounts_form,
        accounts=accounts,
        page=page,
        has_next_page=has_next_page,
    )


@bp.get('/emails')
@login_required
@validate_view
def emails():
    new_email_form = NewAccountForm()
    new_email_form.populate_hosts(current_user.hosts)

    bulk_add_form = BulkAppPasswordForm()
    bulk_add_form.populate_hosts(current_user.hosts)

    if current_user.view == 'admin':
        edit_account_form = AdminEditAccountForm()
        edit_account_form.populate_vps(VPS.get_all())
    else:
        edit_account_form = EditAccountForm()
    return render_template(
        'user/emails.html.j2',
        new_email_form=new_email_form,
        edit_account_form=edit_account_form,
        bulk_add_form=bulk_add_form,
    )


@bp.get('/csv-uploads')
@login_required
@validate_view
def csv_uploads():
    def make_post_request():
        try:
            requests.post(secret_manager.get('CSV_UPLOADS_URL'))
        except Exception as e:
            print(f"Error making POST request: {e}")

    new_form = NewCSVUploadForm()
    new_form.populate_hosts(current_user.hosts)
    user: User = current_user

    if any([csv.status == 'ready' for csv in user.csv_uploads]):
        thread = Thread(target=make_post_request)
        thread.start()

    csv_uploads = sorted(
        user.csv_uploads,
        key=lambda csv: csv.date_uploaded or datetime(1970, 1, 1),
        reverse=True,
    )
    return render_template(
        'user/csv_uploads.html.j2',
        new_form=new_form,
        csv_uploads=csv_uploads,
    )


@bp.get('/dashboard')
@login_required
@validate_view
def dashboard():
    return render_template(
        'dashboard.html.j2',
        title=f'Dashboard',
        iframe_url=current_user.looker_studio_url,
    )


@bp.get('/vps')
@login_required
@validate_view
def vps():
    new_vps_form = VPSForm()
    edit_vps_form = VPSForm()
    machines = VPS.get_all()
    return render_template(
        'user/vps.html.j2',
        machines=machines,
        new_vps_form=new_vps_form,
        edit_vps_form=edit_vps_form,
    )


@bp.get('/seeds')
@login_required
@validate_view
def seeds():
    esps = Account.get_count_per_esp('engagement')
    if current_user.view == 'inboxPlacementAudit':
        base_form = PlacementAuditSeedBatchForm
    else:
        base_form = SeedBatchForm
    Form = form_with_esp_fields(esps, base_form)
    form = Form()

    form.populate_hosts(current_user.hosts)
    user: User = current_user

    def esp_fields(field: Field):
        return field.name.startswith('esp_')

    def first_fields(field: Field):
        return field.name in ["host", "name"]

    def host_fields(field: Field):
        return not esp_fields(field) and not first_fields(field) and field.name != 'generate_type'

    seed_batches = sorted(
        user.seed_batches,
        key=lambda seed_batch: seed_batch.date_added or datetime(1970, 1, 1),
        reverse=True,
    )
    return render_template(
        'user/seeds.html.j2',
        form=form,
        seed_batches=seed_batches,
        esp_fields=esp_fields,
        first_fields=first_fields,
        host_fields=host_fields,
    )


@bp.get('/email-groups')
@login_required
@validate_view
def email_groups():
    assigned_esp = EmailGroup.get_proxy_assigned_count('esp')
    unassigned_esp = EmailGroup.get_proxy_unassigned_count('esp')
    disabled_esp = Account.get_disabled_counts_grouped_by('esp')
    unassigned_server = EmailGroup.get_proxy_unassigned_count('server')

    max_per_esp = mongo.get_config('maxOfServerPerGroup')
    email_groups = EmailGroup.get_all()
    proxies = ProxyDetails.get_all_grouped_by_id()
    servers = Account.distinct(Account._mongo_map['server'])
    esps = [esp.replace(' ', '_')
            for esp in Account.distinct(Account._mongo_map['esp'])]

    proxy_details_form = ProxyDetailsForm()
    update_group_form = UpdateGroupForm()

    return render_template(
        'user/email_groups.html.j2',
        assigned_esp=assigned_esp,
        unassigned_esp=unassigned_esp,
        disabled_esp=disabled_esp,
        unassigned_server=unassigned_server,
        proxy_details_form=proxy_details_form,
        update_group_form=update_group_form,
        max_per_esp=max_per_esp,
        email_groups=email_groups,
        proxies=proxies,
        servers=servers,
        esps=esps,
    )
