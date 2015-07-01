from django.core import exceptions
from django.core.urlresolvers import reverse
from django.conf import settings
from decimal import Decimal
import hashlib

from .models import Transaction


class PayWay(object):
    pgw_language = ''
    pgw_authorization_type = '1'
    pgw_disable_installments = '1'
    pgw_return_method = 'POST'
    pgw_success_url = None
    pgw_failure_url = None

    def __init__(self, request=None, **pgw_data):
        self.request = request
        for x in pgw_data:
            if x.startswith('pgw_'):
                setattr(self, x, pgw_data[x])

    def pgw_data(self):
        return {x: getattr(self, x)
                for x in dir(self) if x.startswith('pgw_')}

    def calc_incoming_signature(self, data):
        """ Calculates hash signature based on incoming request data """
        signature_string = ''
        for item in data:
            signature_string += item
            signature_string += self.pgw_secret_key
        return hashlib.sha512(signature_string.encode('utf-8')).hexdigest()

    def on_success(self):
        pass

    def on_failure(self):
        pass


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

    if isinstance(htpayway_class, str):
        try:
            return import_callable(htpayway_class)
        except AttributeError as e:
            raise exceptions.ImproperlyConfigured(e)
    else:
        return htpayway_class


def begin_transaction(request, pgw_data, htpayway_class=None):
    """ This should be called from your view
        to create Transaction object.
    """

    user = request.user if request.user.is_authenticated() else None
    amount = pgw_data['amount']

    tx = Transaction()
    tx.status = 'created'
    tx.user = user

    """
    result.pgw_shop_id = pgw_data['pgw_shop_id']
    result.pgw_authorization_type = pgw_data['pgw_authorization_type']
    result.pgw_order_id = pgw_data['pgw_order_id']

    result.pgw_first_name = pgw_data.get('pgw_first_name', ''),
    result.pgw_last_name = pgw_data.get('pgw_last_name', ''),
    result.pgw_street = pgw_data.get('pgw_street', ''),
    result.pgw_city = pgw_data.get('pgw_city', ''),
    result.pgw_post_code = pgw_data.get('pgw_post_code', ''),
    result.pgw_country = pgw_data.get('pgw_country', ''),
    result.pgw_email = pgw_data.get('pgw_email', ''),
    """

    payway = get_payway_class(htpayway_class)()
    payway_data = payway.pgw_data()
    for x in payway_data:
        setattr(tx, x, payway_data[x])

    for x in pgw_data:
        if x.startswith('pgw_'):
            setattr(tx, x, pgw_data[x])

    domain = request.get_host()
    if tx.pgw_success_url is None:
        tx.pgw_success_url = u'http://{}{}'.format(domain, reverse('htpayway_success'))
    if tx.pgw_failure_url is None:
        tx.pgw_failure_url = u'http://{}{}'.format(domain, reverse('htpayway_failure'))
    tx.amount = amount
    tx.pgw_amount = format_amount(amount)

    tx.pgw_signature = tx.calc_outgoing_signature()

    tx.save()
    return tx


def format_amount(amount):
    a = Decimal(amount).quantize(Decimal('0.01'))
    return str(a).replace('.', '')
