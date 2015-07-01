# -*- coding: utf-8 -*-
from django.test import TestCase, RequestFactory
from django.core import exceptions
from django.contrib.auth.models import AnonymousUser

from . import PayWay
from .utils import get_payway_class, begin_transaction, format_amount
from .models import Transaction

from decimal import Decimal, InvalidOperation


class CustomPayWay(PayWay):
    pgw_shop_id = '123'
    pgw_secret_key = 'secretkey'
    pgw_success_url = u'http://localhost:8000/payway/success/'
    pgw_failure_url = u'http://localhost:8000/payway/failure/'
    pgw_authorization_type = '0'
    pgw_language = 'hr'


class TestImports(TestCase):
    def test_missing_setting_raises(self):
        with self.assertRaises(exceptions.ImproperlyConfigured):
            get_payway_class('')

    def test_get_payment_class_with_string(self):
        pw = get_payway_class('htpayway.tests.CustomPayWay')()
        self.assertEqual(pw.pgw_shop_id, '123')

    def test_get_payment_class_with_class(self):
        pw = get_payway_class(CustomPayWay)()
        self.assertEqual(pw.pgw_shop_id, '123')


class TestPayWay(TestCase):
    def setUp(self):
        self.payway = CustomPayWay()

    def test_create_signature_for_create(self):
        request = RequestFactory().get('/')
        request.user = AnonymousUser()
        transaction = begin_transaction(
            request, {'pgw_order_id': '1', 'amount': '123.00'},
            htpayway_class=CustomPayWay)

        self.assertEqual(
            transaction.pgw_signature,
            'fc424eb91bb260f8364326629b72de6ef7471cf4d09dc3c998657119cd0df2af' +
            '1f313c21108659e87573b0b6525c74f223b0378ab65dbf3e9ffd84697c31b319'
        )

    def test_pgw_arguments_are_initialized(self):
        p = CustomPayWay(pgw_email='a@a.com')
        self.assertEqual(p.pgw_email, 'a@a.com')

    def test_non_pgw_arguments_are_skipped(self):
        p = CustomPayWay(foo=1)
        self.assertFalse(hasattr(p, 'foo'))

    def test_pgw_data_from_model(self):
        p = Transaction(id=1, pgw_transaction_id=2, pgw_amount='300')
        pgw_data = p.pgw_data()

        self.assertNotIn('id', pgw_data)
        self.assertEqual(pgw_data['pgw_transaction_id'], 2)
        self.assertEqual(pgw_data['pgw_amount'], '300')

    def test_pgw_data_from_class(self):
        p = CustomPayWay(pgw_email='a@a.com')

        self.assertEqual(p.pgw_data()['pgw_email'], 'a@a.com')


class TestUtils(TestCase):
    def test_format_amount_raises_on_non_decimal_input(self):
        with self.assertRaises(InvalidOperation):
            format_amount('')

        with self.assertRaises(TypeError):
            format_amount(None)

    def test_format_amount_with_2_decimal_places(self):
        self.assertEqual(format_amount('123.45'), '12345')

    def test_format_amount_with_3_decimal_places(self):
        self.assertEqual(format_amount(Decimal('1000.123')), '100012')
