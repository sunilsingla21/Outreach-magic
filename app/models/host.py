from __future__ import annotations

from base64 import urlsafe_b64encode
from dataclasses import dataclass, field
from datetime import datetime
from hashlib import sha1

import pytz
from bidict import bidict
from bson import ObjectId
from flask_login import current_user

from app.extensions import mongo, secret_manager
from app.models.account import Account
from app.models.base import BaseModel
from app.models.csv_upload import CSVUpload
from app.models.seed_batch import SeedBatch
from app.utils.urls import generate_looker_studio_url


def engagement_settings_for_audit():
    if not current_user.is_authenticated:
        return False
    return current_user.view != 'inboxPlacementAudit'


@dataclass
class Host(BaseModel):
    def collection(): return mongo.hosts

    _mongo_map = bidict({
        'id': '_id',
        'name': 'host',
        'timezone': 'userSettings.timezone',
        'crypt': 'hostCrypt',

        'instantly_workspace': 'instantly.workspaceId',
        'instantly_api_key': 'instantly.apiKey',

        'smartlead_api_key': 'smartlead.apiKey',
        'smartlead_webhook': 'smartlead.webhook',

        'auto_cc_active': 'autoCc.active',
        'has_custom_auto_cc_message': 'userSettings.hasCustomMessage',
        'auto_cc_message': 'userSettings.ccMessage',
        'cc_name': 'userSettings.ccName',
        'cc_address_string': 'userSettings.ccAddressString',
        'cc_address_array': 'userSettings.ccAddressArray',
        'pronoun_1': 'userSettings.pronoun1',
        'pronoun_2': 'userSettings.pronoun2',

        'notification_address_string': 'userSettings.notificationAddressString',
        'notification_address_array': 'userSettings.notificationAddressArray',

        'total_sent': 'counts.totalSent',
        'total_received': 'counts.totalReceived',
        'counts_last_updated': 'counts.lastUpdated',

        'slack_channel_id': 'slack.notificationChannelId',

        'warmup_tags': 'userSettings.warmupTags',

        'external_sender_addresses': 'userSettings.externalSenderAddresses',

        'auto_exclude_addresses': 'userSettings.autoExcludeAddresses',
        'auto_exclude_usernames': 'userSettings.autoExcludeUsernames',
        'auto_exclude_domains': 'userSettings.autoExcludeDomains',

        'do_not_contact_sheet_url': 'userSettings.doNotContactGoogleSheet',
        'do_not_contact_addresses': 'userSettings.doNotContactAddresses',
        'do_not_contact_domains': 'userSettings.doNotContactDomains',

        'engagement_remove_spam': 'inboxEngagement.removeSpam',
        'engagement_mark_important': 'inboxEngagement.markImportant',
        'engagement_reply_message': 'inboxEngagement.replyMessage',
        'engagement_move_primary': 'inboxEngagement.movePrimary',
        'engagement_click_link': 'inboxEngagement.clickLink',
        'engagement_download_message': 'inboxEngagement.downloadMessage',
        'engagement_scroll_message': 'inboxEngagement.scrollMessage',
    })

    _defaults = {
        'auto_cc_active': False,
        'auto_cc_message': '',
        'has_custom_auto_cc_message': False,

        'external_sender_addresses': lambda: [],

        'auto_exclude_addresses': lambda: mongo.get_config('autoExcludeAddresses'),
        'auto_exclude_usernames': lambda: mongo.get_config('autoExcludeUsernames'),
        'auto_exclude_domains': lambda: mongo.get_config('autoExcludeDomains'),

        'do_not_contact_addresses': lambda: [],
        'do_not_contact_domains': lambda: [],

        'warmup_tags': lambda: [],

        'engagement_remove_spam': engagement_settings_for_audit,
        'engagement_mark_important': engagement_settings_for_audit,
        'engagement_reply_message': False,
        'engagement_move_primary': engagement_settings_for_audit,
        'engagement_click_link': engagement_settings_for_audit,
        'engagement_download_message': engagement_settings_for_audit,
        'engagement_scroll_message': engagement_settings_for_audit,
    }

    _unique_keys = ['name', 'crypt']

    name: str = None
    timezone: str = None
    crypt: str | None = None

    instantly_workspace: str = None
    instantly_api_key: str = None

    smartlead_api_key: str = None
    smartlead_webhook: str = None

    auto_cc_active: bool = _defaults['auto_cc_active']
    has_custom_auto_cc_message: bool = _defaults['has_custom_auto_cc_message']
    auto_cc_message: str = _defaults['auto_cc_message']
    cc_name: str = None
    cc_address_string: str = None
    cc_address_array: list[str] = None
    pronoun_1: str = None
    pronoun_2: str = None

    notification_address_string: str = None
    notification_address_array: list[str] = None

    total_sent: int | None = None
    total_received: int | None = None
    counts_last_updated: datetime | None = None

    __sender_accounts = None
    __csv_uploads = None
    __seed_batches = None

    slack_channel_id: str | None = None

    warmup_tags: list[str] = field(default_factory=list)

    external_sender_addresses: list[str] | None = field(default_factory=list)

    auto_exclude_addresses: list[str] | None = None
    auto_exclude_usernames: list[str] | None = None
    auto_exclude_domains: list[str] | None = None

    do_not_contact_sheet_url: str | None = None
    do_not_contact_addresses: list[str] | None = field(default_factory=list)
    do_not_contact_domains: list[str] | None = field(default_factory=list)

    engagement_remove_spam: bool = field(
        default_factory=_defaults['engagement_remove_spam'],
    )
    engagement_mark_important: bool = field(
        default_factory=_defaults['engagement_mark_important'],
    )
    engagement_reply_message: bool = _defaults['engagement_reply_message']
    engagement_move_primary: bool = field(
        default_factory=_defaults['engagement_move_primary'],
    )
    engagement_click_link: bool = field(
        default_factory=_defaults['engagement_click_link'],
    )
    engagement_download_message: bool = field(
        default_factory=_defaults['engagement_download_message'],
    )
    engagement_scroll_message: bool = field(
        default_factory=_defaults['engagement_scroll_message'],
    )

    id: ObjectId | None = None

    @property
    def looker_studio_url(self):
        return generate_looker_studio_url(current_user.view, self)

    @property
    def sender_accounts(self) -> list[Account]:
        if self.__sender_accounts:
            return self.__sender_accounts
        self.__sender_accounts = Account.get_by_host(self.id)
        return self.__sender_accounts

    @property
    def csv_uploads(self) -> list[CSVUpload]:
        if self.__csv_uploads:
            return self.__csv_uploads
        self.__csv_uploads = CSVUpload.get_by_host(self.id)
        return self.__csv_uploads

    @property
    def seed_batches(self) -> list[CSVUpload]:
        if self.__seed_batches:
            return self.__seed_batches
        self.__seed_batches = SeedBatch.get_by_host(self.id)
        return self.__seed_batches

    def format_counts_last_updated(self):
        if not self.counts_last_updated:
            return ''
        tz = pytz.timezone(self.timezone)
        utc_offset = datetime.now(tz).utcoffset()
        if not utc_offset:
            return ''
        adjusted_date = self.counts_last_updated + utc_offset
        return adjusted_date.strftime('%b %d %H:%M:%S')

    def __parse_address_string(self, string: str):
        if type(string) is str:
            array = [
                address.strip() for address in string.split(',')
            ]
        else:
            array = []
        string = ', '.join(array)
        return string, array

    def __calculate_address_arrays(self):
        self.cc_address_string, self.cc_address_array = self.__parse_address_string(
            self.cc_address_string)

        self.notification_address_string, self.notification_address_array = self.__parse_address_string(
            self.notification_address_string)

    @classmethod
    def _get(cls, obj: dict | None):
        host = super()._get(obj)
        if not host:
            return

        if not host.cc_address_array:
            host.__calculate_address_arrays()

        return host

    @classmethod
    def get_available_host_name_by_company_name(cls, name: str):
        name = name.replace(' ', '_').lower()
        new_name = name
        index = 2
        while True:
            if cls.collection().count_documents({'host': new_name}) == 0:
                return new_name
            new_name = f'{name}{index}'
            index += 1

    def save(self):
        if not self.crypt:
            self.crypt = self.generate_host_crypt(self.name)
        self.__calculate_address_arrays()
        if not self.smartlead_webhook:
            self.smartlead_webhook = secret_manager.get(
                'SMARTLEAD_WEBHOOK_BASE_URL') + self.crypt
        super().save()

    @staticmethod
    def generate_host_crypt(name: str):
        salt: str = secret_manager.get('SECRET_KEY')
        long_hash = sha1((salt + name).encode()).digest()
        encoded_hash = urlsafe_b64encode(long_hash).decode()
        return f'{name}_{encoded_hash[:5]}'

    @classmethod
    def get_by_name(cls, name: str):
        return cls._get(mongo.hosts.find_one({cls._mongo_map.get('name'): name}))

    @classmethod
    def get_by_crypt(cls, crypt: str):
        return cls._get(mongo.hosts.find_one({cls._mongo_map.get('crypt'): crypt}))
