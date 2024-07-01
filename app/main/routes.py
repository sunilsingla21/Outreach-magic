import os
from datetime import datetime, timedelta
from uuid import uuid4

from bson.errors import InvalidId
from flask import (abort, flash, redirect, render_template, request, session,
                   url_for)
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import mongo
from app.main import bp
from app.main.forms import (LoginForm, NewPasswordForm, RegisterForm,
                            ResetPasswordForm)
from app.models import *
from app.utils.emails import (send_approval_email,
                              send_approval_notification_email,
                              send_reset_password_email,
                              send_verification_email)
from app.utils.forms import get_form_error_string
from app.utils.passwords import check_password, hash_password


@bp.get('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    else:
        return redirect(url_for('main.login'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(request.args.get('next') or url_for('user.index'))

    form = LoginForm()
    if not form.validate_on_submit():
        for key in form.errors:
            flash(get_form_error_string(key, form.errors), category='error')
        return render_template('login.html.j2', form=form)

    email = form.email.data
    password = form.password.data
    user = User.get_by_email(email)
    if not user or user and not check_password(password, user.hashed_password):
        flash('Invalid email or password', category='error')
        return render_template('login.html.j2', form=form)

    login_user(user)
    user.login()
    flash('You have successfully logged in')
    return redirect(request.args.get('next') or url_for('user.index'))


@bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password_email():
    token_duration = int(os.getenv('RESET_PASSWORD_TOKEN_DURATION_DAYS'))
    template = 'reset_password.html.j2'
    form = ResetPasswordForm()
    if not form.validate_on_submit():
        for key in form.errors:
            flash(get_form_error_string(key, form.errors), category='error')
        return render_template(template, form=form, type='send-email-form')

    reset_tries = session.get('reset_password', 0)
    reset_date = session.get('reset_password_date')
    if reset_date and reset_date > datetime.utcnow() + timedelta(days=1):
        del session['reset_password_date']
        del session['reset_tries']
        reset_tries = 0

    if reset_tries == 0:
        session['reset_password_date'] = datetime.utcnow()
    if reset_tries > 5:
        return render_template(template, type='limit')
    session['reset_password'] = reset_tries + 1

    user = User.get_by_email(form.email.data)
    if not user:
        return render_template(template, type='submitted')

    is_token_expired = user.token_expiration and datetime.utcnow() > user.token_expiration
    if user.reset_password_token and not is_token_expired:
        send_reset_password_email(user)
        return render_template(template, type='submitted')

    user.reset_password_token = str(uuid4())
    user.token_expiration = datetime.utcnow() + timedelta(days=token_duration)
    user.save()
    send_reset_password_email(user)
    return render_template(template, type='submitted')


@bp.route('/reset-password/<string:id>/<string:token>', methods=['GET', 'POST'])
def reset_password(id: str, token: str):
    redirect_reset = redirect(url_for('main.reset_password_email'))

    try:
        user = User.get_by_id(id)
    except InvalidId:
        flash('Invalid parameters', category='error')
        return redirect_reset

    if not user:
        flash('Invalid parameters', category='error')
        return redirect_reset

    if not user.reset_password_token:
        flash('Invalid reset password request', category='error')
        return redirect_reset

    if datetime.utcnow() > user.token_expiration:
        flash('Your request to reset your password expired. Please try again',
              category='error')
        return redirect_reset

    if user.reset_password_token != token:
        flash('Invalid parameters', category='error')
        return redirect_reset

    form = NewPasswordForm()
    if not form.validate_on_submit():
        for key in form.errors:
            flash(get_form_error_string(key, form.errors), category='error')
        return render_template('reset_password.html.j2', type='new-password-form', form=form)

    user.hashed_password = hash_password(form.password.data)
    user.token_expiration = None
    user.reset_password_token = None
    user.last_password_reset = datetime.utcnow()
    user.save()

    session.pop('reset_password', None)
    session.pop('reset_password_date', None)
    flash('Your password has been reset. You can now login')
    return redirect(url_for('main.login'))


@bp.get('/logout')
def logout():
    logout_user()
    flash('You have successfully logged out')
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    def except_submit(field):
        return field.type != 'SubmitField'

    if current_user.is_authenticated:
        return redirect(url_for('user.index'))
    form = RegisterForm()
    if not form.validate_on_submit():
        for key in form.errors:
            flash(get_form_error_string(key, form.errors), category='error')
        return render_template('register.html.j2', form=form, except_submit=except_submit)

    email = form.email.data
    password = form.password.data
    host_name = Host.get_available_host_name_by_company_name(
        form.company_name.data)

    if User.get_by_email(email):
        flash('Username is already taken', category='error')
        return render_template('register.html.j2', form=form, except_submit=except_submit)

    host = Host(name=host_name, timezone=form.timezone.data)
    host.save()
    user = User.register(email, password, host_ids=[host.id])
    login_user(user)
    flash('User registered successfully')
    return redirect(url_for('main.verify_wall'))


@bp.post('/send-verification')
@login_required
def send_verification():
    if current_user.verified:
        return redirect(url_for('main.index'))
    if current_user.last_verification_sent and current_user.last_verification_sent + timedelta(minutes=5) > datetime.utcnow():
        return render_template('send_verification.html.j2', sent=False)
    sent = send_verification_email(current_user)
    return render_template('send_verification.html.j2', sent=sent)


@bp.get('/verify')
@login_required
def verify_wall():
    if current_user.verified:
        return redirect(url_for('main.index'))
    send_verification_email(current_user)
    return render_template('verify.html.j2')


@bp.get('/verify/<string:id>/<string:token>')
def verify(id: str, token: str):
    redirect_verify = redirect(url_for('main.verify_wall'))

    try:
        user = User.get_by_id(id)
    except InvalidId:
        flash('Invalid parameters', category='error')
        return redirect_verify

    if not user:
        flash('Invalid parameters', category='error')
        return redirect_verify

    if user.verified:
        return redirect(url_for('main.index'))

    if datetime.utcnow() > user.verification_expiration:
        flash('Your request to verify your account expired. Please try again',
              category='error')
        return redirect_verify

    if user.verification_token != token:
        flash('Invalid parameters', category='error')
        return redirect_verify

    user.verified_on = datetime.utcnow()
    user.verified = True
    user.save()
    send_approval_email(user)

    flash('Your account has been verified')
    return redirect(url_for('main.index'))


@bp.get('/approve')
@login_required
def approve_wall():
    if current_user.approved:
        return redirect(url_for('main.index'))
    send_approval_email(current_user)
    return render_template('approve.html.j2')


@bp.get('/approve/<string:id>/<string:token>')
def approve(id: str, token: str):
    redirect_approve = redirect(url_for('main.index'))

    try:
        user = User.get_by_id(id)
    except InvalidId:
        flash('Invalid parameters', category='error')
        return redirect_approve

    if not user:
        flash('User does not exist', category='error')
        return redirect_approve

    if user.approved:
        flash('This user has already been approved', category='info')
        return redirect(url_for('main.index'))

    if datetime.utcnow() > user.approval_expiration:
        flash('The request to approve this account expired. An email will be sent with a new token. Please try again',
              category='error')
        send_approval_email(user)

    if user.approval_token != token:
        flash('Approval tokens do not match', category='error')
        return redirect_approve

    user.approved_on = datetime.utcnow()
    user.approved = True
    user.save()

    flash('The account has been approved')
    send_approval_notification_email(user)
    return render_template('approve.html.j2', approved_user=user, approved=True)


@bp.route('/clear-config-cache', methods=['GET', 'POST'])
@login_required
def clear_config_cache():
    if current_user.view != 'admin':
        abort(403)
    if request.method == 'GET':
        return render_template('clear_config_cache.html.j2')
    mongo.clear_config_cache()
    flash('Cache cleared')
    return redirect(url_for('main.index'))
