from collections import OrderedDict


class AttributeOrderedDict(OrderedDict):
    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, key, value):
        self[key] = value

    @staticmethod
    def create_dict(lst):
        return OrderedDict(zip(lst, [''] * len(lst)))
