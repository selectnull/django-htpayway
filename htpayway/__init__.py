# coding=utf-8
from django.core.urlresolvers import reverse
from collections import OrderedDict
import hashlib


class PayWay(object):
    """
    legend:

        shopid
        secretkey     - sigurnosni kljuc (rucno generirati) - mora se spremiti
        i u PG admin / Shop Managment
        lang          - jezik payment gatewaya (dostupno: hr, en,
                                                de, it, fr, ru)
        authorization_type  - 0 (autorizacija u dva koraka - predautorizacija)
                              1 (autorizacija u jednom koraku - automatska
                                 autorizacija)
        disable_installments  - 1 za onemogucavanje kopovine na rate
        form_url      - url na koji se preusmjerava nakon potvrde
        o placanju kreditnom karticom
        return_method - nacin povrata kupca na ducan. default: post
    """

    pgw_language = 'hr'
    pgw_authorization_type = '1'
    pgw_disable_installments = '1'
    pgw_return_method = 'post'
    pgw_success_url = None
    pgw_failure_url = None

    def create(self, request):
        self.form_url = 'https://pgwtest.ht.hr/services/payment/api/authorize-form'

        # call set_order(order) to change
        self.set_order(None)

        self.set_request(request)

        # iznos u lipama (10 kn = 1000)
        pgw_amount = str(self.order.amount).replace('.', '')

        # url na koji se vraca nakon placanja
        if self.pgw_success_url is None:
            current_domain = request.get_host()
            self.pgw_success_url = 'http://%s%s' %\
                (current_domain, reverse('htpayway_success'))

        if self.pgw_failure_url is None:
            current_domain = request.get_host()
            self.pgw_failure_url = 'http://%s%s' %\
                (current_domain, reverse('htpayway_failure'))

        self.data = OrderedDict([
            ('pgw_shop_id', self.pgw_shop_id),
            ('pgw_order_id', self.order.id),
            ('pgw_amount', pgw_amount),
            ('pgw_authorization_type', self.pgw_authorization_type),
            ('pgw_language', self.pgw_language),
            ('pgw_return_method', self.pgw_return_method),
            ('pgw_success_url', self.pgw_success_url),
            ('pgw_failure_url', self.pgw_failure_url),
            ('pgw_first_name', self.order.first_name),
            ('pgw_last_name', self.order.last_name),
            ('pgw_street', self.order.street),
            ('pgw_city', self.order.city),
            ('pgw_post_code', self.order.post_code),
            ('pgw_country', self.order.country),
            ('pgw_telephone', self.order.telephone),
            ('pgw_email', self.order.email),
            ('pgw_disable_installments', self.pgw_disable_installments),
        ])

        self.data['pgw_signature'] = self.create_signature_for_create()

    def create_signature_for_create(self):
        """
        Signature for seding request to HtPayWay
        """
        signature_string = 'authorize-form' + self.pgw_secret_key
        hash_items = (
            'pgw_shop_id', 'pgw_order_id', 'pgw_amount',
            'pgw_authorization_type', 'pgw_language',
            'pgw_success_url', 'pgw_failure_url'
        )
        for key in hash_items:
            signature_string += self.data[key]
            signature_string += self.pgw_secret_key
        return hashlib.sha512(signature_string).hexdigest()

    def create_signature_for_success(self, **kwargs):
        """
        Signature recieved on success

        """
        items = [kwargs['pgw_trace_ref'], kwargs['pgw_transaction_id'],
                 kwargs['pgw_order_id'], kwargs['pgw_amount'],
                 kwargs['pgw_installments'], kwargs['pgw_card_type_id']]

        signature_string = ''
        for v in items:
            signature_string += v
            signature_string += self.pgw_secret_key
        return hashlib.sha512(signature_string).hexdigest()

    def create_signature_for_failure(self, **kwargs):
        """
        Signature recieved on failure
        """
        items = [kwargs['pgw_result_code'], kwargs['pgw_trace_ref'],
                 kwargs['pgw_order_id']]

        signature_string = ''
        for v in items:
            signature_string += v
            signature_string += self.pgw_secret_key
        return hashlib.sha512(signature_string).hexdigest()

    def set_order(self, order):
        self.order = order

    def set_request(self, request):
        self.request = request

    def on_success(self):
        pass

    def on_failure(self):
        pass
