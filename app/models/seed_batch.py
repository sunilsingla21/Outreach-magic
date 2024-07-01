from __future__ import annotations

import random
import string
from dataclasses import dataclass, field
from datetime import datetime

from bidict import bidict
from bson import ObjectId
from flask import abort, flash
from flask_login import current_user

from app.extensions import mongo
from app.models.base import BaseModel


@dataclass
class SeedBatch(BaseModel):
    def collection(): return mongo.seedBatches

    _insert = True

    _mongo_map = bidict({
        'id': '_id',
        'status': 'status',
        'name': 'name',
        'generate_total': 'generate.total',
        'generate_type': 'generate.type',
        'generate_esps': 'generate.esps',

        'engagement_remove_spam': 'generate.removeSpam',
        'engagement_mark_important': 'generate.markImportant',
        'engagement_reply_message': 'generate.replyMessage',
        'engagement_move_primary': 'generate.movePrimary',
        'engagement_click_link': 'generate.clickLink',
        'engagement_download_message': 'generate.downloadMessage',
        'engagement_scroll_message': 'generate.scrollMessage',

        'prioritize_token': 'generate.prioritizeToken',
        'host_id': 'hostId',
        'token': 'token',
        'results_total': 'results.total',
        'csv_url': 'results.csvUrl',
        'date_added': 'dateAdded',
    })

    status: str = None
    name: str = None
    generate_total: int = None
    generate_type: str = None
    generate_esps: dict[str, int] = field(default_factory=dict)

    engagement_remove_spam: bool = None
    engagement_mark_important: bool = None
    engagement_reply_message: bool = None
    engagement_move_primary: bool = None
    engagement_click_link: bool = None
    engagement_download_message: bool = None
    engagement_scroll_message: bool = None

    prioritize_token: bool | None = None
    host_id: ObjectId = None
    token: str | None = None
    results_total: int | None = None
    csv_url: str | None = None
    date_added: datetime = None

    id: ObjectId | None = None

    def __generate_token(self):
        if self.token:
            return
        chars = string.ascii_letters + string.digits
        while True:
            token = ''.join(
                random.choice(chars)
                for _ in range(5)
            )
            if not self.__class__.collection().find_one({'token': token}):
                break

        self.token = token

    @classmethod
    def get_by_host(cls, host_id):
        collection = cls.collection()
        host_id = cls._object_id(host_id)
        query = collection.find({cls._mongo_map.get('host_id'): host_id})
        return list([cls._get(seed_batch) for seed_batch in query])

    def __prepare_esp_data(self):
        self.generate_total = 0
        for key in self.__dict__:
            if not key.startswith('esp_'):
                continue
            words = key.removeprefix('esp_').split('_')
            esp_camelcase = words[0] + \
                ''.join([word.capitalize() for word in words[1:]])
            count = getattr(self, key)
            self.generate_esps[esp_camelcase] = count
            self.generate_total += count
        if self.generate_total > current_user.assigned_seeds:
            flash('Exceded maximum for assigned seed accounts', category='error')
            abort(400)

    def save(self):
        self.__generate_token()
        self.__prepare_esp_data()
        super().save()
