from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from bidict import bidict
from bson import ObjectId

from app.extensions import mongo
from app.models.base import BaseModel
from app.utils.dict_traverser import DictTraverser


@dataclass
class SmartleadAccount(BaseModel):
    def collection(): return mongo.smartleadEmailAccounts

    _mongo_map = bidict({
        'id': '_id',
        'host_id': 'hostId',
        'host_name': 'hostName',
        'username': 'username',
        'smartlead_client_id': 'smartlead.client_id',
        'smartlead_type': 'smartlead.type',
        'esp': 'esp',
        'last_updated': 'lastUpdated',
    })

    _full_object = 'full_obj'

    host_id: ObjectId
    host_name: str = None
    username: str = None
    smartlead_client_id: int = None
    smartlead_type: str = None
    esp: str = None
    last_updated: datetime = None
    full_obj: DictTraverser = None

    id: ObjectId | None = None

    def save(self):
        self.last_updated = datetime.utcnow()
        super().save()
