# coding=utf-8
import uuid
import random
import hashlib


def randkey():
    return hashlib.md5(''.join(map(str, (uuid.uuid4(), random.random())))).hexdigest()[8:-8]


def table_to_mapping(raw, key, val):
    mapping = {}
    for r in raw:
        mapping[r[key]] = r[val]
    return mapping
