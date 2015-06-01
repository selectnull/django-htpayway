from htpayway import PayWay
from mock import Mock
from decimal import Decimal


class ThisPayWay(PayWay):

    pgw_shop_id = '20000186'
    pgw_secret_key = "pZclhO{2G+RlMR#FWX{9g5'C"

    def set_order(self, order):
        # mock data
        self.order = Mock(name='order')
        self.order.id = '11'
        self.order.first_name = 'Igor'
        self.order.last_name = 'Pejic'
        self.order.address = 'Bujska'
        self.order.city = 'Rijeka'
        self.order.zipcode = '51000'
        self.order.country = 'Hrvatska'
        self.order.phone = '0992347823'
        self.order.email = 'dev-support@logit.hr'
        self.order.total = Decimal('230.30')

    def set_request(self, request):
        self.pgw_language = request.LANGUAGE_CODE

    def after_success(self):
        print 'succesfully overriden success'

    def after_failure(self):
        print 'succesfully overriden failure'
