from future.utils import raise_with_traceback
import json
import sys


class FuzzyHash(object):
    def __init__(self, data, *args, **kwargs):
        self._data = data
        self.counter = 0
        # Check if str then check if JSON.  If JSON, deserialize to a dictionary.
        if isinstance(data, str):
            try:
                self._data = json.loads(data)
            except ValueError:
                pass
        self.type_map = kwargs.get('type_map')
        self.dict_key_ignore = kwargs.get('dict_key_ignore', list())
        self.strict = kwargs.get('strict')

    def __eq__(self, other):
        if not isinstance(other, FuzzyHash):
            other = FuzzyHash(other)
        return self._hash(type_map=self.type_map, strict=self.strict) == other._hash(type_map=self.type_map,
                                                                                     strict=self.strict)

    def __ne__(self, other):
        if not isinstance(other, FuzzyHash):
            other = FuzzyHash(other)
        return self._hash(type_map=self.type_map, strict=self.strict) != other._hash(type_map=self.type_map,
                                                                                     strict=self.strict)

    def __hash__(self):
        return self._hash(type_map=self.type_map, strict=self.strict)

    def __str__(self):
        return str(self._hash(type_map=self.type_map, strict=self.strict))

    def __len__(self):
        return self.count()

    @property
    def data(self):
        return self._data

    def freeze(self, type_map=None, strict=False):
        obj = self._clean(self.data, type_map=type_map)
        return self._nested_freeze(obj=obj, strict=strict)

    def _hash(self, type_map=None, strict=False):
        """
        Makes a hash out of anything that contains only set, tuple, list, dict and hashable types including string and numeric types.
        :param type_map:  Dictionary for mapping type coercion.  e.g. {int: str, float: str} will cast all integers and floats to strings.
                          Useful when working with 3rd party deserialized JSON data where numeric values may be serialized as strings.
        :param strict:  By default, all sets, lists, and tuples are sorted.  To compare order and omit sorting, set to True.
        :return:  Hash representation of the object.
        """
        return self._nested_hash(self.data, type_map=type_map or self.type_map, strict=strict)

    def count(self):
        """
        Return number of objects nested in the data.
        """
        self.counter = 0
        self._count()
        counter = self.counter
        self.counter = 0
        return counter

    def _count(self, **kwargs):
        obj = kwargs.get('obj', self.data)
        level = kwargs.get('level', 0)
        if isinstance(obj, FuzzyHash):
            obj = obj.data
        if isinstance(obj, (set, tuple, list)) and len(obj) > 0:
            length = len([self._count(obj=o or 1, level=level + 1)
                          for o in obj])
            self.counter += length
            return length
        if not isinstance(obj, dict) or not obj:
            return
        length = len([self._count(obj=obj[key] or 1, level=level + 1)
                      for key in obj])
        self.counter += length
        return length

    def _nested_hash(self, obj, type_map=None, strict=False):
        obj = self._clean(obj, type_map=type_map)
        return hash(self._nested_freeze(obj, strict=strict))

    def _clean(self, obj, type_map=None):
        type_map = type_map or self.type_map

        if type_map:
            try:
                cast = type_map[type(obj)]
                if callable(cast):
                    obj = cast(obj)
            except KeyError:
                pass
            except (ValueError, TypeError):  # Raise or ignore?  Maybe allow the strict flag to determine what we do here?
                exc_type, exc_value, exc_traceback = sys.exc_info()
                raise_with_traceback(exc_type(exc_value), exc_traceback)

        if isinstance(obj, (set, tuple, list)):
            return tuple([
                self._clean(value, type_map=type_map)
                for value in obj
            ])
        elif isinstance(obj, dict):
            if len(self.dict_key_ignore):
                for key in self.dict_key_ignore:
                    try:
                        obj.pop(key)
                    except KeyError:
                        pass
            return list({
                key: self._clean(value, type_map=type_map)
                for key, value in obj.items()
            }.items())
        elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes)):
            pass
        return obj

    def _nested_freeze(self, obj, strict=False):
        if isinstance(obj, (set, tuple, list)):
            if not strict:
                obj = sorted(obj)
            return tuple([
                self._nested_freeze(value, strict=strict)
                for value in obj
            ])
        elif isinstance(obj, dict):
            return frozenset(list({
                                 key: self._nested_freeze(value, strict=strict)
                                 for key, value in obj.items()
                             }.items()))
        elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes)):
            pass
        return obj
