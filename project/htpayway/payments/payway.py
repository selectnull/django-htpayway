# coding=utf-8
from django.core.urlresolvers import reverse
from django import forms
from django.contrib.sites.models import Site
import hashlib
from collections import OrderedDict

from htpayway.payments import PaymentGateway
# from webshop.options import get_webshop_app_absolute_url


class PayWay(PaymentGateway):

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

        *** u Shop Managmentu potrebno je ukljuciti opcije
        "Automatsko preusmjeravanje na ReturnURL"
        *** i "Uključi digitalni MD5 potpis"

    example (copy to /project/appsettings.py):

        LOGIT_WEBSHOP_PAYMENT_METHOD = (
            ('kreditna_kartica_payway', 'webshop.payments.payway.Payway', ),
        )

        LOGIT_WEBSHOP_PAYMENT_SETTINGS = {
            'kreditna_kartica_payway': {
                'shopid':          '',
                'secretkey':       '',
                'lang':            'hr',
                'authorization_type':    '0',
                'disable_installments':    '1',
                'return_method': 'post',
                'form_url':
                    https://pgw.ht.hr/services/payment/api/authorize-form',
            }
        }
    """

    def create_signature_for_create(self):
        """
        Signature for seding request to HtPayWay
        """
        secret_key = self.config['secretkey']
        signature_string = 'authorize-form' + secret_key
        for v in self.data.values():
            signature_string += v
            signature_string += secret_key
        return hashlib.sha512(signature_string).hexdigest()

    def create_signature_for_success(self, **kwargs):
        """
        Signature recieved on success

        merchant_data is sent only if it's sent on create so not included
        here
        """
        secret_key = self.config['secretkey']
        items = [kwargs['trace_ref'], kwargs['transaction_id'],
                 kwargs['order_id'], kwargs['amount'],
                 kwargs['installments'], kwargs['card_type_id']]

        signature_string = ''
        for v in items:
            signature_string += v
            signature_string += secret_key
        return hashlib.sha512(signature_string).hexdigest()

    def create_signature_for_failure(self, **kwargs):
        """
        Signature recieved on failure
        """
        secret_key = self.config['secretkey']
        items = [kwargs['pgw_result_code'], kwargs['pgw_trace_ref'],
                 kwargs['pgw_order_id']]

        signature_string = ''
        for v in items:
            signature_string += v
            signature_string += secret_key
        return hashlib.sha512(signature_string).hexdigest()

    def set_order(self, order):
        self.order = order

    def create(self):
        self.set_order(None)
        # iznos u lipama (10 kn = 1000)
        amount = str(self.order.total).replace('.', '')

        # url na koji se vraca nakon placanja
        current_domain = Site.objects.get_current().domain
        success_url = 'http://%s%s' %\
            (current_domain, reverse('transaction_success'))
        success_url = 'http://127.0.0.0:8000/payway/success/'
        failure_url = 'http://%s%s' %\
            (current_domain, reverse('transaction_failure'))
        failure_url = 'http://127.0.0.0:8000/payway/failure/'

        # provjeri ako postoji trazeni prijevod za interface payment gatewaya
        if self.lng not in ('hr', 'en', 'de', 'it', 'fr', 'ru'):
            self.lng = self.config['lang']

        self.data = OrderedDict([
            ('pgw_shop_id', self.config['shopid']),
            ('pgw_order_id', self.order.id),
            ('pgw_amount', amount),
            ('pgw_authorization_type', self.config['authorization_type']),
            ('pgw_language', str(self.lng)),
            ('pgw_return_method', self.config['return_method']),
            ('pgw_success_url', success_url),
            ('pgw_failure_url', failure_url),
            ('pgw_first_name', self.order.first_name),
            ('pgw_last_name', self.order.last_name),
            ('pgw_street', self.order.address),
            ('pgw_city', self.order.city),
            ('pgw_post_code', self.order.zipcode),
            ('pgw_country', self.order.country),
            ('pgw_order_info', self.order.phone),
            ('pgw_email', self.order.email),
            ('pgw_disable_installments', self.config['disable_installments']),
        ])

        self.data['pgw_signature'] = self.create_signature_for_create()

        class PaymentForm(forms.Form):
            pgw_shop_id = forms.CharField(max_length=8)
            pgw_order_id = forms.CharField(max_length=50)
            pgw_amount = forms.CharField(max_length=12)
            pgw_authorization_type = forms.CharField(max_length=1)
            pgw_language = forms.CharField(max_length=2)
            pgw_return_method = forms.CharField(max_length=4)
            pgw_success_url = forms.CharField(max_length=1000)
            pgw_failure_url = forms.CharField(max_length=1000)
            pgw_first_name = forms.CharField(max_length=20)
            pgw_last_name = forms.CharField(max_length=20)
            pgw_street = forms.CharField(max_length=40)
            pgw_city = forms.CharField(max_length=20)
            pgw_post_code = forms.CharField(max_length=9)
            pgw_country = forms.CharField(max_length=50)
            pgw_order_info = forms.CharField(max_length=50)
            pgw_email = forms.CharField(max_length=50)
            pgw_disable_installments = forms.CharField(max_length=1)
            pgw_signature = forms.CharField(max_length=40)

            def __init__(self, *args, **kwargs):
                super(PaymentForm, self).__init__(*args, **kwargs)
                for f in self.fields:
                    self.fields[f].widget = forms.HiddenInput()
                    self.fields[f].required = False

        return PaymentForm(initial=self.data), self.config['form_url']

    def after_success(self):
        print 'after_success_called'
        pass

    def after_failure(self):
        print 'after_failure called'
        pass
