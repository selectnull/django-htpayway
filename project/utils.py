from htpayway import PayWay
from mock import Mock
from decimal import Decimal


class ThisPayWay(PayWay):

    pgw_shop_id = '20000185'
    pgw_secret_key = "pZclhO{2G+RlMR#FWX{9g5'C"

    def set_order(self, order):
        # mock data
        self.order = Mock(name='order')
        self.order.id = '12'
        self.order.first_name = 'Igor'
        self.order.last_name = 'Pejic'
        self.order.street = 'Bujska'
        self.order.city = 'Rijeka'
        self.order.post_code = '51000'
        self.order.country = 'Hrvatska'
        self.order.telephone = '0992347823'
        self.order.email = 'dev-support@logit.hr'
        self.order.amount = Decimal('230.30')
        # url na koji se vraca nakon placanja

    def set_request(self, request):
        self.pgw_language = request.LANGUAGE_CODE

    def on_success(self):
        print 'succesfully overriden success'

    def on_failure(self):
        print 'succesfully overriden failure'
