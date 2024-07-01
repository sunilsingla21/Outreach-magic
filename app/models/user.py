from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from bidict import bidict
from bson import ObjectId
from flask_login import UserMixin

from app.extensions import mongo
from app.models.base import BaseModel
from app.models.csv_upload import CSVUpload
from app.models.host import Host
from app.models.seed_batch import SeedBatch
from app.models.smartlead_account import SmartleadAccount
from app.utils.passwords import hash_password
from app.utils.urls import generate_looker_studio_url


@dataclass
class User(UserMixin, BaseModel):

    def collection(): return mongo.userSettings
    _unique_keys = ['email']

    _defaults = {
        'host_ids': lambda: [],
        'view': 'inboxPlacementAudit',
        'verified': False,
        'approved': False,
        'assigned_seeds': 100,
    }

    _mongo_map = bidict({
        'id': '_id',
        'email': 'appLogin.username',
        'hashed_password': 'appLogin.password',
        'current_login': 'appLogin.currentLogin',
        'last_login': 'appLogin.lastLogin',
        'host_ids': 'hosts',

        'reset_password_token': 'resetPassword.token',
        'last_password_reset': 'resetPassword.lastReset',
        'token_expiration': 'resetPassword.tokenExpiration',

        'verification_token': 'verification.token',
        'verification_expiration': 'verification.tokenExpiration',
        'last_verification_sent': 'verification.lastSent',
        'verified_on': 'verification.verifiedOn',

        'approval_token': 'approval.token',
        'approval_expiration': 'approval.tokenExpiration',
        'last_approval_sent': 'approval.lastSent',
        'approved_on': 'approval.verifiedOn',

        'view': 'appLogin.view',
        'verified': 'appLogin.verified',
        'approved': 'appLogin.approved',

        'assigned_seeds': 'seeds.assignedCount',
    })

    email: str
    hashed_password: str
    id: ObjectId | None = None
    last_login: datetime | None = None
    current_login: datetime = None
    host_ids: list[ObjectId] = field(default_factory=list)
    __hosts = None

    reset_password_token: str | None = None
    last_password_reset: datetime | None = None
    token_expiration: datetime | None = None

    verification_token: str | None = None
    verification_expiration: datetime | None = None
    last_verification_sent: datetime | None = None
    verified_on: datetime | None = None
    verified: bool = _defaults['verified']

    approval_token: str | None = None
    approval_expiration: datetime | None = None
    last_approval_sent: datetime | None = None
    approved_on: datetime | None = None
    approved: bool = _defaults['approved']

    view: str = _defaults['view']

    assigned_seeds: int = _defaults['assigned_seeds']

    def get_smartlead_accounts(self, limit, offset=0):
        accounts = []
        for account in mongo.smartleadEmailAccounts.aggregate([
            {'$match': {'hostId': {'$in': self.host_ids}}},
            {'$skip': offset},
            {'$limit': limit},
        ]):
            accounts.append(SmartleadAccount._get(account))
        return accounts

    @property
    def looker_studio_url(self):
        return generate_looker_studio_url(self.view, *self.hosts)

    @property
    def hosts(self):
        if self.__hosts:
            return self.__hosts
        self.__hosts = Host.get_by_ids(self.host_ids)
        self.host_map = {
            host.id: host
            for host in self.__hosts
        }
        return self.__hosts

    @property
    def csv_uploads(self):
        csv_uploads: list[CSVUpload] = []
        for host in self.hosts:
            for csv_upload in host.csv_uploads:
                csv_uploads.append(csv_upload)
        return csv_uploads

    @property
    def seed_batches(self):
        seed_batches: list[SeedBatch] = []
        for host in self.hosts:
            for seed_batch in host.seed_batches:
                seed_batches.append(seed_batch)
        return seed_batches

    def login(self):
        self.last_login = self.current_login
        self.current_login = datetime.utcnow()
        self.save()

    def has_accounts(self):
        return any([host.sender_accounts for host in self.hosts])

    def has_csv_uploads(self):
        return any([host.csv_uploads for host in self.hosts])

    def has_seed_batches(self):
        return any([host.seed_batches for host in self.hosts])

    def __hosts_changed(self):
        if self.__hosts is None:
            return
        return len(self.hosts) != len(self.host_ids) or \
            any([id != host.id for id, host in zip(self.host_ids, self.hosts)])

    @classmethod
    def _get(cls, obj: dict | None):
        if not obj:
            return None
        user = super()._get(obj)

        # If there is a discrepancy between the IDs and the actual host documents, update IDs
        if user.__hosts_changed():
            user.host_ids = [host.id for host in user.hosts]
            user._has_to_save = True

        if user._has_to_save:
            user.save()

        return user

    @classmethod
    def get_by_email(cls, email: str):
        return cls._get(mongo.userSettings.find_one({'appLogin.username': email}))

    @classmethod
    def register(cls, email: str, password: str, **kwargs):
        hashed_password = hash_password(password)
        user = cls(email=email, hashed_password=hashed_password, **kwargs)
        user.save()
        return user
