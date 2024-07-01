from uuid import uuid4

from flask import (abort, current_app, flash, g, redirect, render_template,
                   request, session, url_for)
from flask_login import login_required

from app.decorators.accounts import validate_host_form, validate_host_session
from app.extensions import microsoft_flow
from app.microsoft import bp
from app.models import *
from app.utils.accounts import validate_added_oauth_account


@bp.post('/login')
@login_required
@validate_host_form
def login():
    state = str(uuid4())
    session['state'] = state

    url = microsoft_flow.get_authorization_request_url(
        scopes=current_app.config.get('MS_SCOPE'),
        state=state,
        redirect_uri=current_app.config.get('MS_REDIRECT_URI'),
    )
    return redirect(url)


@bp.get('/callback')
@login_required
@validate_host_session
def callback():
    if request.args.get('state') != session['state']:
        flash('Invalid state', category='error')
        abort(400)

    response = microsoft_flow.acquire_token_by_authorization_code(
        code=request.args['code'],
        scopes=current_app.config.get('MS_SCOPE'),
        redirect_uri=current_app.config.get('MS_REDIRECT_URI'),
    )
    if 'error' in response:
        flash(response['error_description'], category='error')
        abort(401)

    host: Host = g.host
    email = response['id_token_claims']['preferred_username']
    access_token = response['access_token']
    refresh_token = response['refresh_token']
    name = response['id_token_claims']['name']
    validate_added_oauth_account(
        host=host,
        email=email,
        name=name,
        access_token=access_token,
        refresh_token=refresh_token,
        server='microsoft',
    )
    del session['host']
    session['microsoft_success'] = True
    return redirect(url_for('microsoft.protected_area'))


@bp.get('/protected-area')
@login_required
def protected_area():
    # if 'microsoft_success' not in session:
    #     abort(400)
    # del session['microsoft_success']
    return render_template('microsoft/protected_area.html.j2')
