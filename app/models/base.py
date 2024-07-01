from bson import ObjectId

from app.utils.dict_traverser import DictTraverser


class BaseModel:

    _defaults = {}

    @classmethod
    def _get(cls, obj: dict | None):
        assert '_mongo_map' in cls.__dict__, f'Variable _mongo_map has to be defined for this class: {cls}'
        if obj is None:
            return None

        traverser = DictTraverser(obj)
        fields = {}
        if '_full_object' in cls.__dict__:
            fields[cls._full_object] = traverser
        for key, value in cls._mongo_map.items():
            default = cls._defaults.get(key)
            if callable(default):
                default = default()
            fields[key] = traverser.get(value, default)

        obj: cls = cls(**fields)
        obj._has_to_save = False
        return obj

    def save(self):
        assert '_mongo_map' in self.__class__.__dict__, f'Variable _mongo_map has to be defined for this class: {self.__class__}'
        collection = type(self).collection()
        update = {}
        for mongo_key, key in self._mongo_map.inverse.items():
            default = self._defaults.get(key)
            if callable(default):
                default = default()
            update[mongo_key] = getattr(self, key)
            if update[mongo_key] is None:
                update[mongo_key] = default

        del update['_id']

        if self.id:
            collection.update_one(
                filter={'_id': self.id},
                update={'$set': update},
            )
        elif '_insert' in self.__class__.__dict__ and self.__class__._insert:
            result = collection.insert_one({})
            self.id = result.inserted_id
            result = collection.update_one(
                filter={'_id': self.id},
                update={'$set': update},
                upsert=True,
            )
        else:
            assert '_unique_keys' in self.__class__.__dict__, f'Variable _unique_keys has to be defined for this class: {self.__class__}'
            filter = {
                self._mongo_map[unique_key]: getattr(self, unique_key)
                for unique_key in self._unique_keys
            }
            result = collection.update_one(
                filter=filter,
                update={'$set': update},
                upsert=True,
            )
            self.id = result.upserted_id

    def delete(self):
        assert '_delete' in self.__class__.__dict__ and self.__class__._delete == True, f'This class does not allow deletion: {self.__class__}'
        collection = type(self).collection()
        result = collection.delete_one({
            '_id': self.id,
        })
        assert result.deleted_count == 1

    @classmethod
    def get(cls, filter: dict | None = None):
        collection = cls.collection()
        if not filter:
            filter = {}
        return cls._get(collection.find_one(filter))

    @classmethod
    def get_all(cls, filter: dict | None = None):
        collection = cls.collection()
        if not filter:
            filter = {}
        return [cls._get(item) for item in collection.find(filter)]

    @classmethod
    def count(cls, *args, **kwargs):
        # TODO: refactor count_documents calls with this function
        return cls.collection().count_documents(*args, **kwargs)

    @classmethod
    def distinct(cls, *args, **kwargs):
        return cls.collection().distinct(*args, **kwargs)

    @classmethod
    def update_many(cls, **kwargs):
        collection = cls.collection()
        return collection.update_many(**kwargs)

    @classmethod
    def get_by_id(cls, id: str | ObjectId):
        collection = cls.collection()
        id = cls._object_id(id)
        query = collection.find_one({'_id': id})
        return cls._get(query)

    @classmethod
    def get_by_ids(cls, ids: list[ObjectId]):
        collection = cls.collection()
        query = collection.find({'_id': {
            '$in': ids
        }})
        return [cls._get(item) for item in query]

    def _object_id(id: str | ObjectId):
        if type(id) is str:
            return ObjectId(id)
        elif type(id) is ObjectId:
            return id
        else:
            raise ValueError(f'Invalid ObjectId: {id}')
