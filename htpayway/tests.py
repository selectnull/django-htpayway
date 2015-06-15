# -*- coding: utf-8 -*-
from django.test import TestCase
from django.core import exceptions

from htpayway import PayWay
from htpayway.utils import get_payway_class

from mock import Mock


class CustomPayWay(PayWay):

    pgw_shop_id = '123'
    pgw_secret_key = 'secretkey'
    pgw_success_url = 'http://www.mojducan.com/success/narudžba456'
    pgw_failure_url = 'http://www.mojducan.com/failure/narudžba456'
    pgw_authorization_type = '0'

    def set_order(self, order):
        # mock data
        self.order = Mock(name='order')
        self.order.id = 'narudžba456'
        self.order.first_name = None
        self.order.last_name = None
        self.order.street = None
        self.order.city = None
        self.order.post_code = None
        self.order.country = None
        self.order.telephone = None
        self.order.email = None
        self.order.amount = 789

    def set_request(self, request):
        self.pgw_language = ''


class TestImports(TestCase):
    def test_missing_setting_raises(self):
        with self.assertRaises(exceptions.ImproperlyConfigured):
            get_payway_class('')

    def test_get_payment_class(self):
        pw = get_payway_class('htpayway.tests.CustomPayWay')()
        self.assertEqual(pw.pgw_shop_id, '123')


class TestCustomPayWay(TestCase):

    def setUp(self):
        self.custompw = CustomPayWay()
        self.custompw.set_order(None)
        self.custompw.create(None)

    def test_create_signature_for_create(self):
        self.assertEqual('8295bfece351e248e73870ad10ffb9dc63abd807582e5fdd4348'
                         'd12284f6b8cc13e93eaa502034c1cb4114ddc84f'
                         '19868d4ebfff55682e0c521a96a5022974cb',
                         self.custompw.data['pgw_signature'])
