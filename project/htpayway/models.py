from django.db import models
from django.contrib.auth.models import User


STATUS = (
    ('su', 'Success'),
    ('fa', 'Failure'),
)


class Transaction(models.Model):
    transaction_id = models.CharField(max_length=10)
    user = models.ForeignKey(User, null=True)
    shop_id = models.CharField(max_length=8)
    order_id = models.CharField(max_length=50)
    amount = models.CharField(max_length=12)
    authorization_type = models.CharField(max_length=1)
    signature = models.CharField(max_length=128)

    # if response is recieved with vaild signature success = True
    success = models.BooleanField()

    status = models.CharField(max_length=2, choices=STATUS)
