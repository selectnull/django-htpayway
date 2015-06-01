""" Utility functions for dynamic import. """
from django.core import exceptions


def import_callable(callable_path):
    try:
        dot = callable_path.rindex('.')
    except ValueError:
        raise exceptions.ImproperlyConfigured,\
            "%s isn't a callable ([package.[module.]]callable)" % callable_path
    module_name, callable_name = callable_path[:dot], callable_path[dot + 1:]
    try:
        mod = __import__(module_name, {}, {}, [''])
    except ImportError, e:
        raise exceptions.ImproperlyConfigured,\
            'Error importing module %s: "%s"' % (module_name, e)
    try:
        return getattr(mod, callable_name)
    except AttributeError:
        raise exceptions.ImproperlyConfigured,\
            'Module "%s" does not define a "%s" callable' %\
            (module_name, callable_name)


def import_callable_or_none(callable_path):
    try:
        return import_callable(callable_path)
    except exceptions.ImproperlyConfigured:
        return None
