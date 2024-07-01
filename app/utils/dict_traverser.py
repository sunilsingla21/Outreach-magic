class DictTraverser:
    def __init__(self, obj: dict, null_value=None):
        self.__obj = obj
        self.NULL_VALUE = null_value

    def get(self, key: str, default=None):
        if default is None:
            default = self.NULL_VALUE

        sub_obj = self.__obj
        sub_key = key
        for sub_key in key.split('.'):
            if sub_key not in sub_obj or sub_obj[sub_key] is None:
                return default
            sub_obj = sub_obj[sub_key]

        return sub_obj
