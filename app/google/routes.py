import google.auth.transport.requests
import requests
from flask import (abort, current_app, flash, g, redirect, render_template,
                   request, session, url_for)
from flask_login import login_required
from google.oauth2 import id_token
from pip._vendor import cachecontrol

from app.account.forms import AddAccountAppPasswordForm
from app.decorators.accounts import validate_host_form, validate_host_session
from app.extensions import google_flow
from app.google import bp
from app.models import Host
from app.utils.accounts import validate_added_oauth_account


@bp.post('/add')
@login_required
@validate_host_form
def add():
    host: Host = g.host
    form = AddAccountAppPasswordForm()
    form.host_id.data = str(host.id)
    form.server.data = 'google'
    return render_template('google/add/index.html.j2', form=form)


@bp.get('/login')
@login_required
@validate_host_session
def login():
    authorization_url, state = google_flow.authorization_url(
        access_type='offline',
        prompt='consent',
    )
    session['state'] = state
    return redirect(authorization_url)


@bp.get('/callback')
@login_required
@validate_host_session
def callback():
    host: Host = g.host
    try:
        google_flow.fetch_token(authorization_response=request.url)
    except Warning:
        flash('You have to tick the box to allow email access. Please try again',
              category='error')
        abort(400)

    if session['state'] != request.args['state']:
        flash('The state doesn\'t match, please try again', category='error')
        abort(400)  # State does not match!

    credentials = google_flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(
        session=cached_session
    )

    id_info = id_token.verify_oauth2_token(
        id_token=credentials.id_token,
        request=token_request,
        audience=current_app.config.get('GOOGLE_CLIENT_ID')
    )

    email = id_info['email']
    name = id_info['name']
    validate_added_oauth_account(
        host=host,
        email=email,
        name=name,
        access_token=credentials.token,
        refresh_token=credentials.refresh_token,
        server='google',
    )

    del session['host']
    session['google_success'] = True

    return redirect(url_for('google.protected_area'))


@bp.get('/protected-area')
@login_required
def protected_area():
    if 'google_success' not in session:
        abort(400)
    del session['google_success']
    return render_template('google/protected_area/index.html.j2')
