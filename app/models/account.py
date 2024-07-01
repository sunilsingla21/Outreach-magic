from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache

from bidict import bidict
from bson import ObjectId

from app.extensions import mongo
from app.models.base import BaseModel
from app.utils.accounts import calculate_esp
from app.utils.time import previous_minute_multiple


@dataclass
class Account(BaseModel):
    def collection(): return mongo.emailAccounts

    _unique_keys = ['username']
    _delete = True

    _defaults = {
        'placement_account_active': False,
        'inbox_placement_active': False,

        'engagement_account_active': False,
        'inbox_engagement_active': False,

        'inbox_reset': False,

        'relay_account': False,
    }
    _mongo_map = bidict({
        'id': '_id',
        'host_id': 'hostId',
        'username': 'username',
        'server': 'server',
        'esp': 'esp',
        'esp_camel_case': 'espCamelCase',
        'sender_name': 'senderName',
        'connection_type': 'connectionType',
        'status': 'status',
        'email_group_id': 'emailGroupId',

        'placement_account_active': 'placementAccount.active',
        'inbox_placement_active': 'inboxPlacement.active',

        'engagement_account_active': 'engagementAccount.active',
        'inbox_engagement_active': 'inboxEngagement.active',

        'engagement_via': 'engagementAccount.via',

        'inbox_reset': 'emailReporting.inboxReset',

        'relay_account': 'relayAccount.active',

        'machine_id': 'vpsDetails.machineId',
        'vps_name': 'vpsDetails.machineName',

        'last_updated_password': 'lastUpdatedPassword',
        'last_updated_2fa': 'lastUpdated2fa',

        'app_password': 'appPassword',
        'access_token': 'accessToken',
        'refresh_token': 'refreshToken',

        'smtp_result': 'testResults.smtp',
        'imap_result': 'testResults.imap',
        'tests_last_updated': 'testResults.lastUpdated',

        'time_added': 'timeAdded',
        'last_updated': 'lastUpdated',
        'time_created': 'timeCreated',
    })

    host_id: ObjectId = None
    username: str = None
    server: str = None
    esp: str = None
    esp_camel_case: str = None
    sender_name: str = None
    connection_type: str = None
    status: str = None
    email_group_id: ObjectId | None = None

    placement_account_active: bool = _defaults['placement_account_active']
    inbox_placement_active: bool = _defaults['inbox_placement_active']

    engagement_account_active: bool = _defaults['engagement_account_active']
    inbox_engagement_active: bool = _defaults['inbox_engagement_active']

    engagement_via: str = None

    inbox_reset: bool = _defaults['inbox_reset']

    relay_account: bool = _defaults['relay_account']

    machine_id: str | None = None
    vps_name: str | None = None

    last_updated_password: datetime | None = None
    last_updated_2fa: datetime | None = None

    app_password: str | None = None
    access_token: str | None = None
    refresh_token: str | None = None

    smtp_result: bool | None = None
    imap_result: bool | None = None
    tests_last_updated: datetime | None = None

    time_added: datetime | None = None
    last_updated: datetime | None = None
    time_created: datetime | None = None

    id: ObjectId | None = None

    @classmethod
    def get_by_email(cls, email: str):
        collection = cls.collection()
        result = collection.find_one({'username': email})
        return cls._get(result)

    @classmethod
    def get_by_host(cls, host_id: str | ObjectId):
        collection = cls.collection()
        host_id = cls._object_id(host_id)
        query = collection.find({cls._mongo_map.get('host_id'): host_id})
        return list([cls._get(acc) for acc in query])

    @classmethod
    def organize_esps(cls, pipeline):
        result = cls.collection().aggregate(pipeline)
        esps = {}
        for document in result:
            esps[document['_id'].replace(' ', '_')] = document['accumulator']
        return esps

    @classmethod
    def pipeline_group_by(cls, group_by='esp', accumulator={'$sum': 1}):
        return [
            {
                '$group': {
                    '_id': f'${cls._mongo_map[group_by]}',
                    'accumulator': accumulator,
                },
            },
            {
                '$sort': {
                    '_id': 1,
                },
            },
        ]

    @classmethod
    def get_disabled_counts_grouped_by(cls, group_by):
        pipeline = [
            {
                '$match': {
                    '$or': [
                        {cls._mongo_map['engagement_account_active']: True},
                        {cls._mongo_map['placement_account_active']: True},
                    ],
                    cls._mongo_map['status']: 'disabled',
                },
            },
            *cls.pipeline_group_by(group_by),
        ]
        return cls.organize_esps(pipeline)

    @classmethod
    @lru_cache
    def __cached_get_count_per_esp(cls, account_type, _):
        pipeline = [
            {
                '$match': {
                    f'{account_type}Account.active': True,
                    'status': 'active',
                    'testResults.imap': True,
                    'testResults.smtp': True,
                },
            },
            *cls.pipeline_group_by(),
        ]
        return cls.organize_esps(pipeline)

    @classmethod
    def get_count_per_esp(cls, account_type):
        return cls.__cached_get_count_per_esp(account_type, previous_minute_multiple(datetime.utcnow(), 15))

    def __calculate_esp(self):
        if self.esp and self.esp_camel_case:
            return
        esp, esp_camel_case = calculate_esp(self.username, self.server)
        self.esp = esp
        self.esp_camel_case = esp_camel_case

    def save(self):
        self.last_updated = datetime.utcnow()
        self.__calculate_esp()
        super().save()

    def delete(self):
        from app.models import EmailGroup
        super().delete()
        if self.email_group_id:
            group = EmailGroup.get_by_id(self.email_group_id)
            group.calculate_server_counts()
            group.save()
