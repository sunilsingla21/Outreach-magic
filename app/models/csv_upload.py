from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from bidict import bidict
from bson import ObjectId

from app.extensions import mongo
from app.models.base import BaseModel


@dataclass
class CSVUpload(BaseModel):
    def collection(): return mongo.csvUploads

    _insert = True

    _mongo_map = bidict({
        'id': '_id',
        'host_id': 'hostId',
        'import_name': 'importName',
        'import_source': 'importSource',

        'company_created': 'results.company.created',
        'company_updated': 'results.company.updated',
        'company_ignored': 'results.company.ignored',

        'person_created': 'results.person.created',
        'person_updated': 'results.person.updated',
        'person_ignored': 'results.person.ignored',

        'errors': 'results.errors',

        'date_uploaded': 'dateUploaded',
        'last_updated': 'lastUpdated',

        'update_existing': 'updateExisting',
        'status': 'status',
        'csv_link': 'csvLink',
    })

    host_id: ObjectId
    import_name: str
    import_source: str

    date_uploaded: datetime

    update_existing: bool
    status: str

    csv_link: str | None = None
    last_updated: datetime | None = None

    company_created: int | None = None
    company_updated: int | None = None
    company_ignored: int | None = None

    person_created: int | None = None
    person_updated: int | None = None
    person_ignored: int | None = None

    errors: int | None = None

    id: ObjectId | None = None

    @classmethod
    def get_by_host(cls, host_id: str | ObjectId):
        collection = cls.collection()
        host_id = cls._object_id(host_id)
        query = collection.find({cls._mongo_map.get('host_id'): host_id})
        return list([cls._get(acc) for acc in query])

    def save(self):
        self.last_updated = datetime.utcnow()
        super().save()
