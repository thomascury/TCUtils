from typing import get_type_hints
import types


def strict_types(function):
    def type_checker(*args, **kwargs):
        hints = get_type_hints(function)

        all_args = kwargs.copy()
        all_args.update(dict(zip(function.__code__.co_varnames, args)))

        for argument, argument_type in ((i, type(j)) for i, j in all_args.items()):
            if argument in hints:
                if not issubclass(argument_type, hints[argument]):
                    raise TypeError('Type of {} is {} and not {}'.format(argument, argument_type, hints[argument]))

        result = function(*args, **kwargs)

        if 'return' in hints:
            if type(result) != hints['return']:
                raise TypeError('Type of result is {} and not {}'.format(type(result), hints['return']))

        return result

    return type_checker


def check_types(function):
    def type_checker(*args, **kwargs):
        print("\nChecking type hints for {}".format(function))
        hints = get_type_hints(function)

        all_args = kwargs.copy()
        all_args.update(dict(zip(function.__code__.co_varnames, args)))

        for argument, argument_type in ((i, type(j)) for i, j in all_args.items()):
            if argument in hints:
                if not issubclass(argument_type, hints[argument]):
                    print('Type of {} is {}, hint is {}'.format(argument, argument_type, hints[argument]))

        result = function(*args, **kwargs)

        if 'return' in hints:
            # Use issubclass for a soft type check or type(result) for a hard check
            # if not issubclass(type(result), hints['return']):
            if type(result) != hints['return']:
                print('Type of result is {}, hint is {}'.format(type(result), hints['return']))

        return result

    return type_checker


class CheckFunctionTypeMetaClass(type):
    def __new__(mcs, name, bases, attrs):
        for attr_name, attr_value in attrs.items():
            if isinstance(attr_value, types.FunctionType):
                attrs[attr_name] = check_types(attr_value)
        return super(CheckFunctionTypeMetaClass, mcs).__new__(mcs, name, bases, attrs)


class EnforceFunctionTypeMetaClass(type):
    def __new__(mcs, name, bases, attrs):
        for attr_name, attr_value in attrs.items():
            if isinstance(attr_value, types.FunctionType):
                attrs[attr_name] = strict_types(attr_value)
        return super(EnforceFunctionTypeMetaClass, mcs).__new__(mcs, name, bases, attrs)
