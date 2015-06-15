""" Utility functions for dynamic import. """

from django.core import exceptions
from django.conf import settings


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


def get_payway_class(htpayway_class=None):
    if htpayway_class is None:
        htpayway_class = settings.HTPAYWAY_CLASS
    try:
        return import_callable(htpayway_class)
    except AttributeError as e:
        raise exceptions.ImproperlyConfigured(e)
