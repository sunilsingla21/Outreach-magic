from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache

from bidict import bidict
from bson import ObjectId
from pymongo import UpdateOne

from app.extensions import mongo
from app.models.account import Account
from app.models.base import BaseModel
from app.models.proxy_details import ProxyDetails
from app.utils.time import previous_minute_multiple


@dataclass
class EmailGroup(BaseModel):
    def collection(): return mongo.emailGroups

    _insert = True

    _defaults = {
        'account_ids': lambda: [],
    }

    _mongo_map = bidict({
        'id': '_id',
        'proxy_id': 'proxyDetailsId',
        'server_counts': 'counts',
    })

    proxy_id: ObjectId | None = None
    server_counts: dict[str, int] = None

    id: ObjectId | None = None

    @classmethod
    def _get(cls, obj: dict | None):
        if not obj:
            return None
        group = super()._get(obj)
        if not group.server_counts:
            group.calculate_server_counts()
            group.save()

        return group

    def calculate_server_counts(self):
        if not self.id:
            raise Exception(
                'Tried to get counts for a non yet existing EmailGroup')
        self.server_counts = Account.organize_esps([
            {
                '$match': {
                    Account._mongo_map['email_group_id']: self.id,
                },
            },
            *Account.pipeline_group_by('server'),
        ])

    @classmethod
    def assign_unassigned(cls, status=None):
        bulk_updates = []
        max_per_esp = mongo.get_config('maxOfServerPerGroup')
        groups = cls.get_all()
        groups_iter = _EmailGroupIterator(groups)

        accounts_to_assign_grouped_by_esp = cls.__get_unassigned_account_ids(
            status)
        groups_to_save: list[cls] = []
        for esp, ids in accounts_to_assign_grouped_by_esp.items():
            groups_iter.restart()
            current_group = next(groups_iter)
            for id in ids:
                while (available_count := current_group.server_counts.get(esp, 0)) >= max_per_esp:
                    current_group = next(groups_iter)

                bulk_updates.append(
                    UpdateOne(
                        filter={'_id': id},
                        update={
                            '$set': {
                                Account._mongo_map['email_group_id']: current_group.id,
                            },
                        },
                    )
                )
                current_group.server_counts[esp] = available_count + 1
                groups_to_save.append(current_group)

        for group in groups_to_save:
            group.save()

        if not bulk_updates:
            return 0
        return Account.collection().bulk_write(bulk_updates).modified_count

    @classmethod
    def reassign_proxy(cls, proxy_id):
        groups = cls.get_all({cls._mongo_map['proxy_id']: proxy_id})
        bulk_updates = []
        for group, proxy in zip(groups, _ProxiesIterator([proxy_id])):
            bulk_updates.append(
                UpdateOne(
                    filter={'_id': group.id},
                    update={
                        '$set': {
                            cls._mongo_map['proxy_id']: proxy.id,
                        },
                    },
                )
            )
        if not bulk_updates:
            return
        EmailGroup.collection().bulk_write(bulk_updates)

    @classmethod
    def __get_unassigned_account_ids(cls, status):
        pipeline = [
            {
                '$match': {
                    Account._mongo_map['status']: status or {'$exists': True},
                    '$or': [
                        {Account._mongo_map['engagement_account_active']: True},
                        {Account._mongo_map['placement_account_active']: True},
                    ],
                    Account._mongo_map['email_group_id']: {'$eq': None},
                },
            },
            *Account.pipeline_group_by('server', {'$push': '$_id'}),
        ]
        return Account.organize_esps(pipeline)

    @classmethod
    def __pipeline_for_proxy_count(cls, status, assigned, group_by):
        match = {
            '$or': [
                {Account._mongo_map['engagement_account_active']: True},
                {Account._mongo_map['placement_account_active']: True},
            ],
            Account._mongo_map['status']: status or {'$exists': True},
            Account._mongo_map['email_group_id']: {
                '$ne' if assigned else '$eq': None,
            },
        }
        return [
            {'$match': match},
            *Account.pipeline_group_by(group_by),
        ]

    @classmethod
    def invalidate_caches(cls):
        cls.__cached_get_proxy_assigned_count.cache_clear()
        cls.__cached_get_proxy_unassigned_count.cache_clear()

    @classmethod
    @lru_cache
    def __cached_get_proxy_unassigned_count(cls, status, group_by, _):
        pipeline = cls.__pipeline_for_proxy_count(status, False, group_by)
        return Account.organize_esps(pipeline)

    @classmethod
    def get_proxy_unassigned_count(cls, group_by, status=None):
        return cls.__cached_get_proxy_unassigned_count(status, group_by, previous_minute_multiple(datetime.utcnow(), 15))

    @classmethod
    @lru_cache
    def __cached_get_proxy_assigned_count(cls, status, group_by, _):
        pipeline = cls.__pipeline_for_proxy_count(status, True, group_by)
        return Account.organize_esps(pipeline)

    @classmethod
    def get_proxy_assigned_count(cls, group_by, status=None):
        return cls.__cached_get_proxy_assigned_count(status, group_by, previous_minute_multiple(datetime.utcnow(), 15))


class _ProxiesIterator:
    def __init__(self, exclude=[]):
        self.proxies = ProxyDetails.get_all({
            '_id': {'$nin': exclude}
        })
        self.index = -1

    def __iter__(self):
        return self

    def __next__(self):
        self.index += 1
        self.index %= len(self.proxies)
        return self.proxies[self.index]


class _EmailGroupIterator:
    def __init__(self, groups: list[EmailGroup]):
        self.__index = -1
        self.__proxies = _ProxiesIterator()
        self.__groups = groups

    def restart(self):
        self.__index = -1

    def __next__(self):
        self.__index += 1
        if self.__index >= len(self.__groups):
            next_proxy = next(self.__proxies)
            new_group = EmailGroup(proxy_id=next_proxy.id)
            new_group.save()
            self.__groups.append(new_group)
        return self.__groups[self.__index]
