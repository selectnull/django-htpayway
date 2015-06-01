from django.db import models
from django.contrib.auth.models import User


STATUS = (
    ('created', 'Created'),
    ('succeeded', 'Succeeded'),
    ('failed', 'Failed'),
)


class Transaction(models.Model):
    pgw_transaction_id = models.CharField(max_length=10)

    created_on = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(User, null=True, blank=True)
    pgw_shop_id = models.CharField(max_length=8)
    pgw_order_id = models.CharField(max_length=50)
    pgw_amount = models.CharField(max_length=12)
    pgw_authorization_type = models.CharField(max_length=1)
    pgw_signature = models.CharField(max_length=128)
    pgw_first_name = models.CharField(max_length=20)
    pgw_last_name = models.CharField(max_length=20)
    pgw_street = models.CharField(max_length=40)
    pgw_city = models.CharField(max_length=20)
    pgw_post_code = models.CharField(max_length=9)
    pgw_country = models.CharField(max_length=50)
    pgw_email = models.CharField(max_length=50)

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    status = models.CharField(max_length=10, choices=STATUS)

    response_received_on = models.DateTimeField(null=True, blank=True)
    response_signature_valid = models.BooleanField(default=False)

    class Meta:
        db_table = 'htpayway_transactions'

    def __unicode__(self):
        return u'{} {}'.format(self.user, self.created_on)
