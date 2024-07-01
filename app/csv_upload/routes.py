from datetime import datetime

from flask import flash, redirect, url_for
from flask_login import current_user, login_required

from app.csv_upload import bp
from app.csv_upload.forms import NewCSVUploadForm
from app.extensions import secret_manager
from app.models import *
from app.utils.files import upload_to_bucket
from app.utils.forms import get_form_error_string


@bp.post('')
@login_required
def create():
    response = redirect(url_for('user.csv_uploads'))
    form = NewCSVUploadForm()
    form.populate_hosts(current_user.hosts)
    if not form.validate_on_submit():
        for key in form.errors:
            flash(get_form_error_string(key, form.errors), category='error')
        return response

    host = Host.get_by_id(form.host.data)
    if not host or host.id not in current_user.host_ids:
        flash('Invalid host', category='error')
        return response

    csv_upload = CSVUpload(
        host_id=host.id,
        import_name=form.import_name.data,
        import_source=form.import_source.data,
        date_uploaded=datetime.utcnow(),
        update_existing=form.update_existing.data,
        status='ready',
    )
    csv_upload.save()
    csv_link = upload_to_bucket(
        f'{csv_upload.id}.csv',
        form.csv_file.data,
        secret_manager.get('CSV_UPLOADS_BUCKET'),
    )
    csv_upload.csv_link = csv_link
    csv_upload.save()
    flash('CSV file uploaded successfully')
    return response
