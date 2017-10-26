from functools import wraps


def fast_memoize_one_arg(f):
    class MemoDict(dict):
        __slots__ = ()

        def __missing__(self, key):
            self[key] = ret = f(key)
            return ret
    return MemoDict().__getitem__


def fast_memoize_plus_args(f):
    class MemoDict(dict):
        __slots__ = ()

        def __missing__(self, key):
            self[key] = ret = f(*key)
            return ret
    return MemoDict().__getitem__


def fast_memoize_no_args(func):
    class MemoDict(dict):
        __slots__ = ()

        def __missing__(self, key):
            self[key] = ret = func()
            return ret

        def __getitem__(self, _):
            return dict.__getitem__(self, func.__name__)
    return MemoDict().__getitem__


def fast_memoize_any_args(func):
    class MemoDict(dict):
        __slots__ = ()
        __token__ = object()

        def __missing__(self, key):
            self[key] = ret = key == self.__token__ and func() or isinstance(key, list) and func(*key) or func(key)
            return ret

        def __getitem__(self, *args):
            args = len(args) > 0 and args or self.__token__
            return dict.__getitem__(self, args)
    return MemoDict().__getitem__


def memoize(func):
    """A simple fast_memoize decorator for functions supporting positional args."""
    cache = func.cache = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        key = (args, frozenset(sorted(kwargs.items())))
        try:
            return cache[key]
        except KeyError:
            ret = cache[key] = func(*args, **kwargs)
        return ret

    return wrapper
