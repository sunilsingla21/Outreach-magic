import os
from datetime import datetime, timedelta
from uuid import uuid4

import requests
from flask import url_for

from app.extensions import secret_manager
from app.models import User


def _send_email(
    to: str,
    template_id='d-c80c540d168e48ea9d9aa8e95614f541',
    **data,
):
    """
    Send email using Sendgrid API
        Parameters:
            data (dict): Values to send under "dynamic_template_data" to Sendgrid
            Expects values such as: first_name, subject, headline, message, button_label, button_url
    """
    url = secret_manager.get('SENDGRID_SEND_URL')
    headers = {
        'Authorization': f'Bearer {secret_manager.get("SENDGRID_TOKEN")}',
        'Content-Type': 'application/json',
    }
    data = {
        'from': {
            'email': secret_manager.get('EMAIL_FROM_ADDRESS'),
            'name': secret_manager.get('EMAIL_FROM_NAME'),
        },
        'personalizations': [
            {
                'to': [
                    {
                        'email': to,
                    },
                ],
                'dynamic_template_data': data,
            },
        ],
        'template_id': template_id,
    }
    response = requests.post(
        url,
        headers=headers,
        json=data,
    )
    response.raise_for_status()


def send_reset_password_email(user: User):
    reset_password_url = secret_manager.get('BASE_URL') + \
        url_for('main.reset_password', id=user.id,
                token=user.reset_password_token)
    _send_email(
        user.email,
        first_name=user.email,
        subject='Reset password',
        headline='Reset password',
        message='Please click the button below to reset your password.',
        button_label='Reset password',
        button_url=reset_password_url,
    )


def send_verification_email(user: User):
    def send_email():
        verify_email_url = secret_manager.get('BASE_URL') + \
            url_for('main.verify', id=user.id, token=user.verification_token)
        _send_email(
            user.email,
            first_name=user.email,
            subject='Verify email',
            headline='Verify email',
            message='Please click the button below to verify your email.',
            button_label='Verify email',
            button_url=verify_email_url
        )
    is_token_expired = user.verification_expiration and \
        datetime.utcnow() > user.verification_expiration
    token_duration = int(os.getenv('VERIFICATION_TOKEN_DURATION_DAYS'))
    if user.verification_token and not is_token_expired:
        if user.last_verification_sent + timedelta(minutes=5) < datetime.utcnow():
            send_email()
            return True
        else:
            return False

    user.verification_token = str(uuid4())
    user.verification_expiration = datetime.utcnow() + timedelta(days=token_duration)
    user.last_verification_sent = datetime.utcnow()
    send_email()
    user.save()
    return True


def send_approval_email(user: User):
    def send_email():
        approve_account_url = secret_manager.get('BASE_URL') + \
            url_for('main.approve', id=user.id, token=user.approval_token)
        _send_email(
            secret_manager.get('APPROVAL_EMAIL_TO'),
            first_name=secret_manager.get('APPROVAL_EMAIL_TO_NAME'),
            subject=f'{user.email} webApp registration',
            headline=f'{user.email} webApp registration',
            message=f'{user.email} is pending approval. Click the button below to approve this account.',
            button_label='Approve account',
            button_url=approve_account_url,
        )
    if user.approved:
        return False

    is_token_expired = user.approval_expiration and \
        datetime.utcnow() > user.approval_expiration
    token_duration = int(os.getenv('APPROVAL_TOKEN_DURATION_DAYS'))
    if user.approval_token and not is_token_expired:
        return False

    user.approval_token = str(uuid4())
    user.approval_expiration = datetime.utcnow() + timedelta(days=token_duration)
    user.last_approval_sent = datetime.utcnow()
    send_email()
    user.save()
    return True


def send_approval_notification_email(user: User):
    index_url = secret_manager.get('BASE_URL') + url_for('main.index')
    _send_email(
        user.email,
        first_name=user.email,
        subject='Your account has been approved!',
        headline='Your account has been approved!',
        message='You can now start using your Outreach Magic account!',
        button_label='Go to the app',
        button_url=index_url,
    )
