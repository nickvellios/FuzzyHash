# FuzzyHash
Deep nested hashing of Python objects.

Out of the box object freezing and hashing in Python does not generate a unique hash for nested iterables and mixed types.
JSON responses from web servers contain inconsistencies and cannot be compared in their string form, or as hashes.  Inconsistencies
in JSON can develop from a service's type inference, as well as in dictionary key or list order.
e.g. 1 == 1.0 == '1' == '1.0', but 1 !== 1.0 !== '1' !== '1.0'

FuzzyHash allows for both strict type and order hashing, as well as both type coercion and object manipulation prior to hashing.

1.) By default, lists and tuples are sorted before hashing, but passing in `strict = True` will respect their order, opting out of sorting.

2.) Type coercion prior to hashing can be done for all levels in a nested object by passing in a dictionary as `type_map` to __init__.
    An example type map would be {int: unicode, float: unicode, str: unicode}.  All integers, floats, and strings will be cast to unicode strings
    before hashing.

Functions can be passed as type map values

### For example:
```
from types import NoneType

def none_to_zero_len_str(value):
    return ''

def to_upper(string):
    return string.upper()

some_object_1 = {'name': 'Bob Evans', 'title': ''}
some_object_2 = {'name': 'BOB EVANS', 'title': None}
type_map = {str: to_upper, NoneType: none_to_zero_len_str}
hash_object_1 = FuzzyHash(some_object_1, type_map=type_map)
hash_object_2 = FuzzyHash(some_object_2, type_map=type_map)
hash_object_1 == hash_object_2
```
```
>>> True
```

3.) Dictionary keys can be ignored by passing a list of keys as `dict_key_ignore` to __init__.  Example usage would be for API response timestamps.
    Note:  Not all objects are hashable.  JSON strings passed to __init__'s on data parameter will be deserialized into a native Python object.

### Examples:
```
some_object_1 = {'name': 'Bob Evans', 'title': '', 'edit_log': ['2020-05-01 12:29:25.984355', '2020-05-03 13:05:22.338301', '2020-05-29 19:01:51.871108']}
some_object_2 = {'name': 'Bob Evans', 'edit_log': []}
hash_object_1 = FuzzyHash(some_object_1, type_map=type_map)
hash_object_2 = FuzzyHash(some_object_2, type_map=type_map)
hash_object_1 == hash_object_2
```
```
>>> False
```
```
hash_object_1 = FuzzyHash(some_object_1, type_map=type_map, dict_key_ignore=['title', 'edit_log'])
hash_object_2 = FuzzyHash(some_object_2, type_map=type_map, dict_key_ignore=['title', 'edit_log'])
hash_object_1 == hash_object_2
```
```
>>> True
```
