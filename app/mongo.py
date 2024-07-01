from datetime import datetime
from functools import lru_cache, wraps

from flask_pymongo import PyMongo

from app.utils.time import previous_hour_multiple


def print_name(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if False:
            print(f'Accessing {f.__name__}')
        return f(*args, **kwargs)
    return decorated_function


class Mongo(PyMongo):

    @property
    def v4(self):
        'Direct access to v4 database'
        return self.cx.v4

    @property
    @print_name
    def userSettings(self):
        return self.v4.userSettings

    @property
    @print_name
    def hosts(self):
        return self.v4.hosts

    @property
    @print_name
    def emailAccounts(self):
        return self.v4.emailAccounts

    @property
    @print_name
    def smartleadEmailAccounts(self):
        return self.v4.smartleadEmailAccounts

    @property
    @print_name
    def emailsSent(self):
        return self.v4.emailsSent

    @property
    @print_name
    def emailsReceived(self):
        return self.v4.emailsReceived

    @property
    @print_name
    def csvUploads(self):
        return self.v4.csvUploads

    @property
    @print_name
    def vpsMachines(self):
        return self.v4.vpsMachines

    @property
    @print_name
    def seedBatches(self):
        return self.v4.seedBatches

    @property
    @print_name
    def emailGroups(self):
        return self.v4.emailGroups

    @property
    @print_name
    def proxyDetails(self):
        return self.v4.proxyDetails

    @property
    @print_name
    def config(self):
        return self.v4.config

    @lru_cache
    def __get_config(self, key, date):
        document = self.config.find_one({'key': key})
        if not document:
            raise ValueError(f'Could not find config value for key "{key}"')
        return document['value']

    def get_config(self, key: str):
        return self.__get_config(key, previous_hour_multiple(datetime.utcnow(), 24))

    def clear_config_cache(self):
        self.__get_config.cache_clear()
