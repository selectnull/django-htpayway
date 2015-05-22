# coding=utf-8
from django.core.urlresolvers import reverse
from django import forms
from django.contrib.sites.models import Site
import md5
from collections import OrderedDict

from htpayway.payments import PaymentGateway
# from webshop.options import get_webshop_app_absolute_url


class PayWay(PaymentGateway):

    """
    legend:

        shopid
        secretkey     - sigurnosni kljuc (rucno generirati) - mora se spremiti i u PG admin / Shop Managment
        lang          - jezik payment gatewaya (dostupno: hr, en, de, it, fr, ru)
        authorization_type  - 0 (autorizacija u dva koraka - predautorizacija)
                              1 (autorizacija u jednom koraku - automatska autorizacija
        disable_installments  - 1 za onemogucavanje kopovine na rate
        form_url      - url na koji se preusmjerava nakon potvrde o placanju kreditnom karticom
        return_method - nacin povrata kupca na ducan. default: post

        *** u Shop Managmentu potrebno je ukljuciti opcije "Automatsko preusmjeravanje na ReturnURL"
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
                'form_url': https://pgw.ht.hr/services/payment/api/authorize-form',
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
        return md5.new(signature_string).hexdigest()

    def create_signature_for_success(self, **kwargs):
        """
        Signature recieved on success

        merchant_data is sent only if it's sent on create so not included
        here
        """
        secret_key = self.config['secretkey']
        signature_string = 'authorize-form' + secret_key
        items = [kwargs['trace_ref'], kwargs['transaction_id'],
                 kwargs['order_id'], kwargs['amount'],
                 kwargs['installments'], kwargs['card_type_id']]

        for v in items:
            signature_string += v
            signature_string += secret_key
        return md5.new(signature_string).hexdigest()

    def create_signature_for_failure(self, **kwargs):
        """
        Signature recieved on failure
        """
        secret_key = self.config['secretkey']
        signature_string = 'authorize-form' + secret_key
        items = [kwargs['result_code'], kwargs['trace_ref'],
                 kwargs['order_id']]

        for v in items:
            signature_string += v
            signature_string += secret_key
        return md5.new(signature_string).hexdigest()

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
            ('ShopID', self.config['shopid']),
            ('OrderID', self.order.id),
            ('Amount', amount),
            ('AuthorizationType', self.config['authorization_type']),
            ('Language', str(self.lng)),
            ('ReturnMethod', self.config['return_method']),
            ('SuccessURL', success_url),
            ('FailureURL', failure_url),
            ('CustomerFirstname', self.order.first_name),
            ('CustomerSurname', self.order.last_name),
            ('CustomerAddress', self.order.address),
            ('CustomerCity', self.order.city),
            ('CustomerZIP', self.order.zipcode),
            ('CustomerCountry', self.order.country),
            ('CustomerPhone', self.order.phone),
            ('CustomerEmail', self.order.email),
            ('DisableInstallments', self.config['disable_installments']),
        ])

        self.data['Signature'] = self.create_signature_for_create()

        class PaymentForm(forms.Form):
            ShopID = forms.CharField(max_length=8)
            OrderID = forms.CharField(max_length=50)
            Amount = forms.CharField(max_length=12)
            AuthorizationType = forms.CharField(max_length=1)
            Language = forms.CharField(max_length=2)
            ReturnMethod = forms.CharField(max_length=4)
            SuccessURL = forms.CharField(max_length=1000)
            FailureURL = forms.CharField(max_length=1000)
            CustomerFirstname = forms.CharField(max_length=20)
            CustomerSurname = forms.CharField(max_length=20)
            CustomerAddress = forms.CharField(max_length=40)
            CustomerCity = forms.CharField(max_length=20)
            CustomerZIP = forms.CharField(max_length=9)
            CustomerCountry = forms.CharField(max_length=50)
            CustomerPhone = forms.CharField(max_length=50)
            CustomerEmail = forms.CharField(max_length=50)
            DisableInstallments = forms.CharField(max_length=1)
            Signature = forms.CharField(max_length=40)

            def __init__(self, *args, **kwargs):
                super(PaymentForm, self).__init__(*args, **kwargs)
                for f in self.fields:
                    self.fields[f].widget = forms.HiddenInput()
                    self.fields[f].required = False

        return PaymentForm(initial=self.data), self.config['form_url']

    def check(self, request, credit_card_note=''):
        if request.method != self.config['request_method']:
            return False

        pg_id = request.GET.get('tid')
        pg_card_name = request.GET.get('card')
        # iznos u lipama (10 kn = 1000)
        amount = str(self.order.total).replace('.', '')

        # kreiranje potpisa
        signature = self.create_signature_for_create()

        # ako je placanje uspjesno
        if str(signature).upper() == str(request.GET.get('sig')).upper():
            credit_card_note = 'TID: %s, CreditCard: %s' % (pg_id,
                                                            pg_card_name)

        return super(Payway, self).check(request, credit_card_note)

    def after_success(self):
        pass

    def after_failure(self):
        pass
