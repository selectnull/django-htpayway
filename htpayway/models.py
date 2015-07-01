# coding=utf-8
from django.db import models
from django.contrib.auth.models import User

import hashlib


STATUS = (
    ('created', 'Created'),
    ('succeeded', 'Succeeded'),
    ('failed', 'Failed'),
)

CARD_TYPES = (
    ('1', 'American Express'),
    ('2', 'MasterCard'),
    ('3', 'Visa'),
    ('4', 'Diners'),
    ('5', 'Maestro'),
)


class Transaction(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS)
    user = models.ForeignKey(User, null=True, blank=True)

    pgw_shop_id = models.CharField(max_length=8, blank=True)
    pgw_order_id = models.CharField(max_length=50)
    pgw_amount = models.CharField(max_length=12)
    pgw_authorization_type = models.CharField(max_length=1, blank=True)
    pgw_language = models.CharField(max_length=2, blank=True)
    pgw_success_url = models.CharField(max_length=1000)
    pgw_failure_url = models.CharField(max_length=1000)

    pgw_first_name = models.CharField(max_length=20, blank=True)
    pgw_last_name = models.CharField(max_length=20, blank=True)
    pgw_street = models.CharField(max_length=40, blank=True)
    pgw_city = models.CharField(max_length=20, blank=True)
    pgw_post_code = models.CharField(max_length=9, blank=True)
    pgw_country = models.CharField(max_length=50, blank=True)
    pgw_telephone = models.CharField(max_length=50, blank=True)
    pgw_email = models.CharField(max_length=50, blank=True)
    pgw_disable_installments = models.CharField(max_length=1, blank=True)

    pgw_signature = models.CharField(max_length=128, blank=True)

    pgw_result_code = models.CharField(max_length=4, blank=True)
    pgw_trace_ref = models.CharField(max_length=200, blank=True)
    pgw_transaction_id = models.CharField(max_length=10, blank=True)
    pgw_installments = models.CharField(max_length=10, blank=True)
    pgw_card_type_id = models.CharField(
        max_length=2, choices=CARD_TYPES,
        null=True, blank=True, default=None)

    response_received_on = models.DateTimeField(null=True, blank=True)
    response_signature_valid = models.BooleanField(default=False)

    class Meta:
        db_table = 'htpayway_transactions'

    def __unicode__(self):
        return u'{} {} {} {} {} {:.2f} kn'.format(
            self.pgw_transaction_id, self.pgw_first_name,
            self.pgw_last_name, self.user,
            self.created_on,
            self.amount
        )

    def pgw_data(self):
        return {x.name: getattr(self, x.name)
                for x in self._meta.fields if x.name.startswith('pgw_')}

    def calc_outgoing_signature(self):
        """ Calculates hash signature for outgoing request """

        signature_string = u'authorize-form' + self.pgw_secret_key
        fields = (
            'pgw_shop_id', 'pgw_order_id', 'pgw_amount',
            'pgw_authorization_type', 'pgw_authorization_token', 'pgw_language',
            'pgw_return_method', 'pgw_success_url', 'pgw_failure_url',
            'pgw_first_name', 'pgw_last_name', 'pgw_street', 'pgw_city',
            'pgw_post_code', 'pgw_country', 'pgw_telephone', 'pgw_email',
            'pgw_disable_installments'
        )

        for key in fields:
            value = getattr(self, key, None)
            if value is not None:
                signature_string += value
                signature_string += self.pgw_secret_key
        return hashlib.sha512(signature_string.encode('utf-8')).hexdigest()
