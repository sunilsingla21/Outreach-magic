from __future__ import annotations

from dataclasses import dataclass

from bidict import bidict
from bson import ObjectId

from app.extensions import mongo
from app.models.base import BaseModel


@dataclass
class ProxyDetails(BaseModel):
    def collection(): return mongo.proxyDetails

    _insert = True
    _delete = True

    _mongo_map = bidict({
        'id': '_id',
        'ip': 'ip',
        'port': 'port',
        'username': 'username',
        'password': 'password',
        'string': 'string',
    })

    ip: str
    port: int
    username: str
    password: str
    string: str = None

    id: ObjectId | None = None

    def save(self):
        self.string = f'{self.ip}:{self.port}:{self.username}:{self.password}'
        super().save()

    @classmethod
    def get_all_grouped_by_id(cls):
        return {
            proxy.id: proxy
            for proxy in cls.get_all()
        }

    @classmethod
    def from_string(cls, string: str):
        obj = cls(*string.split(':'))
        obj.port = int(obj.port)
        return obj

    def delete(self):
        from app.models.email_group import EmailGroup
        EmailGroup.reassign_proxy(self.id)
        super().delete()
