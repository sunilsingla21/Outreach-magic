from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timedelta

from bidict import bidict
from bson import ObjectId

from app.extensions import mongo
from app.models.base import BaseModel


@dataclass
class VPS(BaseModel):
    def collection(): return mongo.vpsMachines

    _insert = True

    _mongo_map = bidict({
        'id': '_id',
        'name': 'name',
        'status': 'status',
        'machine_id': 'id',
        'hardware': 'hardware',
        'provider': 'provider',
        'last_seen_online': 'lastSeenOnline',
        'last_success': 'lastSuccess',
        'inbox_engagement_ready': 'counts.inboxEngagementReady',
        'inbox_engagement_success': 'counts.inboxEngagementSuccess',
        'inbox_engagement_error': 'counts.inboxEngagementError',
        'counts_last_updated': 'counts.lastUpdated',
    })

    name: str = None
    status: str = None
    machine_id: str = None
    hardware: str = None
    provider: str = None
    last_seen_online: datetime = None
    last_success: datetime = None

    inbox_engagement_ready: int = None
    inbox_engagement_success: int = None
    inbox_engagement_error: int = None
    counts_last_updated: datetime = None

    id: ObjectId | None = None

    @classmethod
    def _get(cls, obj: dict | None):
        vps = super()._get(obj)
        if not vps:
            return
        # vps.__calculate_counts()
        # if vps._has_to_save:
        #     vps.save()

        return vps

    def __calculate_counts_status(self, status):
        return mongo.emailsReceived.count_documents({
            'inboxEngagement.status': status,
            'email.receiverAddress': {
                '$in': self.__accounts,
            }
        })

    def __calculate_counts(self):
        cache_duration = os.getenv('VPS_CACHE_DURATION_MINUTES')
        delta = timedelta(minutes=int(cache_duration))
        now = datetime.utcnow()
        if self.counts_last_updated and self.counts_last_updated + delta >= now:
            return

        self.__accounts = [
            account['username']
            for account in mongo.emailAccounts.find({
                'vpsDetails.machineId': self.machine_id,
            })
        ]
        self.inbox_engagement_ready = self.__calculate_counts_status('ready')
        self.inbox_engagement_success = self.__calculate_counts_status(
            'success')
        self.inbox_engagement_error = self.__calculate_counts_status('error')
        self.counts_last_updated = datetime.utcnow()
        self._has_to_save = True
