from django.db import models
from django.contrib.auth.models import User


STATUS = (
    ('su', 'Success'),
    ('fa', 'Failure'),
)


class Transaction(models.Model):
    pgw_transaction_id = models.CharField(max_length=10)
    user = models.ForeignKey(User, null=True)
    pgw_shop_id = models.CharField(max_length=8)
    pgw_order_id = models.CharField(max_length=50)
    pgw_amount = models.CharField(max_length=12)
    pgw_authorization_type = models.CharField(max_length=1)
    pgw_signature = models.CharField(max_length=128)

    # if response is recieved with vaild signature success = True
    success = models.BooleanField()

    status = models.CharField(max_length=2, choices=STATUS)
