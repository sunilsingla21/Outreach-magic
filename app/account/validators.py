from datetime import datetime

from bson import ObjectId
from flask import flash

from app.config import Config
from app.extensions import mongo
from app.models import Account
from app.utils.forms import update_data_from_form


class ValidBulkAccounts(object):
    def __init__(self, message=None):
        if not message:
            message = "Field must contain valid line separated values"
        self.message = message

    def __process_line(self, line: str):
        email, password, name, server = [l.strip() for l in line.split(':')]

        count = mongo.emailAccounts.count_documents({
            'username': email,
        }) + mongo.smartleadEmailAccounts.count_documents({
            'username': email,
        })
        if count > 0:
            flash(f'{email} is already present in database', category='error')
            return
        if server not in Config.VALID_SERVERS:
            flash(
                f'Server "{server}" not valid for account {email}', category='error')
            return
        account = Account(
            host_id=ObjectId(self.form.host.data),
            username=email,
            sender_name=name,
            server=server,
            app_password=password,
            connection_type='App Password',
            time_added=datetime.utcnow(),
        )
        update_data_from_form(account, self.form, keys_to_ignore=[
                              'host_id', 'accounts'])
        return account

    def __call__(self, form, field):
        if type(field.data) is not list:
            return
        self.form = form
        lines: list[str] = field.data
        accounts = []
        for line in lines:
            account = self.__process_line(line)
            if account:
                accounts.append(account)
        field.data = accounts
