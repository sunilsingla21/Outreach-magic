from datetime import datetime

from flask import abort, flash

from app.extensions import mongo


def validate_added_oauth_account(
    *,
    host,
    email: str,
    name: str,
    access_token: str,
    refresh_token: str,
    server: str,
):
    from app.models import Account
    existing_account = Account.get_by_email(email)
    if existing_account and existing_account.host_id != host.id:
        flash('This account has already been added to a different host',
              category='error')
        existing_account.access_token = access_token
        existing_account.refresh_token = refresh_token
        existing_account.save()
        abort(400)

    if existing_account:
        account = existing_account
        flash('This email account had already been added before', category='info')
    else:
        account = Account(
            host_id=host.id,
            username=email,
            server=server,
            status='active',
            connection_type='OAuth',
            time_added=datetime.utcnow()
        )

    account.sender_name = name
    account.access_token = access_token
    account.refresh_token = refresh_token
    account.save()


def calculate_esp(username, server):
    personal_domains = mongo.get_config(f'{server}PersonalDomains')
    domain = username.split('@')[1]
    esp = 'personal' if domain in personal_domains else 'business'

    return (
        f'{server} {esp}',
        f'{server}{esp.capitalize()}',
    )
