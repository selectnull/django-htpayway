from htpayway import PayWay
from mock import Mock


class ThisPayWay(PayWay):

    pgw_shop_id = '20000186'
    pgw_secret_key = "pZclhO{2G+RlMR#FWX{9g5'C"

    def set_order(self, order):
        # mock data
        self.order = Mock(name='order')
        self.order.total = '2000'
        self.order.id = '11'
        self.order.first_name = 'Igor'
        self.order.last_name = 'Pejic'
        self.order.address = 'Bujska'
        self.order.city = 'London'
        self.order.zipcode = '3342'
        self.order.country = 'Zimbabwe'
        self.order.phone = '0992347823'
        self.order.email = 'igor.pejic@dr.com'
        self.order.total = 230.30

    def set_request(self, request):
        self.pgw_language = request.LANGUAGE_CODE

    def after_success(self):
        print 'succesfully overriden success'

    def after_failure(self):
        print 'succesfully overriden failure'
