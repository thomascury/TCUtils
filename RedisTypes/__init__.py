from collections import Iterable
from typing import Dict, Generator

from RedisTypes.RedisDB import RedisDB
from tcutils.type_hinting import CheckFunctionTypeMetaClass


def _retype(bytestring: bytes):
        s = str(bytestring)[2:-1]
        if s.isnumeric():
            s = int(s)
        return s


# For type_hinting debugging, add metaclass:
# class RedisType(metaclass=CheckFunctionTypeMetaClass)
#  or for throwing exceptions on bad type:
# class RedisType(metaclass=EnforceFunctionTypeMetaClass)
class RedisType:
    def __init__(self, name: str, redisdb: RedisDB):
        if not isinstance(redisdb, RedisDB):
            raise TypeError("Please provide a correct RedisDB.")
        self._name = name
        self._db = redisdb


class InitializationError(BaseException):
    pass


class dict(RedisType):
    """
    http://redis.io/commands#hash
    """
    @classmethod
    def fromdict(cls, name: str, redisdb: RedisDB, dico: dict) -> dict:
        """
        Generates a tcutils.RedisTypes.dict from a builtin type dict
        :param name: str
        :param redisdb: RedisDB.RedisDB
        :param dico: dict
        :return: tcutils.RedisTypes.dict
        """
        command = "HMSET {}".format(name)
        for key in dico.keys():
            command += " {} {}".format(key, dico.get(key))
        if not redisdb.execute(command) == b'OK':
            raise InitializationError("Could not initialize hash on database")
        return cls(name, redisdb)

    def __setitem__(self, key: object, value: object) -> bool:
        """
        :param key: object
        :param value: object
        :return: boolean
        """
        command = "HSET {} {} {}".format(self._name, key, value)
        return self._db.execute(command) == 0

    def __getitem__(self, item: object) -> object:
        """
        :param item: object
        :return: object
        """
        command = "HGET {} {}".format(self._name, item)
        return _retype(self._db.execute(command))

    def __repr__(self) -> str:
        """
        :return: string
        """
        command = "HGETALL {}".format(self._name)
        result = self._db.execute(command)
        dico = {}
        for index, item in enumerate(result):
            if index % 2 == 0:
                key = _retype(item)
            else:
                dico[key] = _retype(item)
        return str(dico)

    def __str__(self) -> str:
        """
        :return: string
        """
        return self.__repr__()

    def __delitem__(self, key: object) -> bool:
        """
        :param key: object
        :return: boolean
        """
        command = "HDEL {} {}".format(self._name, key)
        return self._db.execute(command) == 0

    def __contains__(self, item: object) -> bool:
        """
        :param item: object
        :return: boolean
        """
        command = "HEXISTS {} {}".format(self._name, item)
        return self._db.execute(command) == 1

    def __len__(self) -> int:
        """
        :return: int
        """
        command = "HLEN {}".format(self._name)
        return self._db.execute(command)

    def __del__(self) -> bool:
        """
        :return: boolean
        """
        command = "DEL {}".format(self._name)
        return self._db.execute(command) == 0

    def __iter__(self) -> Generator:
        """
        :return: object
        """
        command = "HKEYS {}".format(self._name)
        keys = self._db.execute(command)
        for key in [_retype(key) for key in keys]:
            yield key

    def keys(self) -> list:
        """
        :return: list
        """
        command = "HKEYS {}".format(self._name)
        keys = self._db.execute(command)
        keys = [_retype(key) for key in keys]
        return keys

    def values(self) -> list:
        """
        :return: list
        """
        command = "HVALS {}".format(self._name)
        values = self._db.execute(command)
        values = [_retype(value) for value in values]
        return values

    def items(self) -> list:
        """
        :return: list
        """
        command = "HGETALL {}".format(self._name)
        result = self._db.execute(command)
        items = []
        for index, item in enumerate(result):
            if index % 2 == 0:
                key = _retype(item)
            else:
                value = _retype(item)
                items.append((key, value))
        return items

    def update(self, dico: dict) -> bool:
        """
        :param dico: dict
        :return: boolean
        """
        if not isinstance(dico, Dict):
            raise TypeError("Please provide a correct dictionary object.")
        if len(dico) == 0:
            return True
        command = "HMSET {}".format(self._name)
        for key in dico.keys():
            command += " {} {}".format(key, dico.get(key))
        return self._db.execute(command) == b'OK'


class list(RedisType):
    """
    TODO
    http://redis.io/commands#list
    """
    @classmethod
    def fromlist(cls, name, redisdb, lst):
        command = "RPUSH {}".format(name)
        for item in lst:
            command += " {}".format(item)
        redisdb.execute(command) == b'OK'
        return cls(name, redisdb)

    def append(self, item):
        command = "RPUSH {}".format(self._name)
        return self._db.execute(command) == 0

    def update(self, iterable: Iterable):
        if not isinstance(iterable, Iterable):
            TypeError("Please provide a valid iterable object.")
        if len(iterable) == 0:
            return True
        command = "RPUSH {}".format(self._name)
        for item in iterable:
            command += " {}".format(item)
        return self._db.execute(command) == b'OK'


def testdict():
    db = RedisDB("127.0.0.1")
    print(_retype(db.execute("ECHO 'Hello'")))
    dico = {
        "TYPEMAGASIN": 0,
        "NUMEROTICKET": 1,
        "NUMEROCOMMANDE": 2,
        "DATEFACTURATION": 6,
        "STATUTTICKET": 5,
        "COMMENTAIRE": 7
    }
    dico = dict.fromdict("FIELDSBYNAME", db, dico)
    print(dico)
    dico["TYPEMAGASIN"] = 1
    print(dico["TYPEMAGASIN"])
    dico["TYPEMAGASIN"] = 0
    print("TYPEMAGASIN" in dico)
    print(dico.keys())
    print(len(dico))
    print(dico.values())
    print(dico.items())
    for key in dico:
        print(key)
    print(dico.update({}))


def testlist():
    db = RedisDB("127.0.0.1")
    print(_retype(db.execute("ECHO 'Hello'")))

if __name__ == '__main__':
    testdict()
