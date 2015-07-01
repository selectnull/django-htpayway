# coding=utf-8
import hashlib


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
