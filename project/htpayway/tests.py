from django.test import TestCase

from mock import Mock

from payments.payway import PayWay


class CustomPayWay(PayWay):

    def __init__(self, lng):
        self.lng = 'hr'
        self.config = {}
        self.config['shopid'] = '20000186'
        self.config['secretkey'] = "pZclhO{2G+RlMR#FWX{9g5'C"
        self.config['lang'] = 'hr'
        self.config['authorization_type'] = '1'
        self.config['return_method'] = 'post'
        self.config['disable_installments'] = '1'
        self.config['form_url'] =\
            'https://pgwtest.ht.hr/services/payment/api/authorize-form'

    def set_order(self, order):
        # mock data
        self.order = Mock(name='order')
        self.order.id = '10'
        self.order.first_name = 'Igor'
        self.order.last_name = 'Pejic'
        self.order.address = 'Bujska'
        self.order.city = 'London'
        self.order.zipcode = '3342'
        self.order.country = 'Zimbabwe'
        self.order.phone = '0992347823'
        self.order.email = 'sd@dfds.com'
        self.order.total = 230.30


class TestCustomPayWay(TestCase):

    def setUp(self):
        self.custompw = CustomPayWay('hr')
        self.custompw.set_order(None)
        self.a = self.custompw.create()
        print self.a

    def test_create_signature_for_create_ok(self):
        pass
