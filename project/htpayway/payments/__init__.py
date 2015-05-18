from django.conf import settings
#from webshop.models.status import StatusCommon
#from webshop.options import STATUS_PAYMENT_SUCCESS, STATUS_CANCELED
from datetime import datetime


class PaymentGateway(object):
    """
    legend:

        extra_tax      - dodatna cijena/popust u postotku za odabrani nacin placanja

    example (copy to /project/appsettings.py):
        '<payment_code>': {
            'extra_tax':       0.05, # ili negativna vrijednost za popust
        },
    """

    def __init__(self, lng, code):
        self.lng = lng

        try:
            self.config = settings.LOGIT_WEBSHOP_PAYMENT_SETTINGS[code]
        except KeyError:
            self.config = None

    def create(self):
        # kreiranje obrasca sa podacima za pocetak placanja kreditnom karticom
        "return form_fields, form_action"

    def check(self, request, credit_card_note=''):
        # provjera rezultata transakcije
        if len(credit_card_note) > 0:
            self.order.admin_notes = '%s\nPayment: %s, %s' % ( self.order.admin_notes,
                datetime.now().strftime("%d.%m.%y %H:%M"), credit_card_note)
            #self.order.status = StatusCommon.objects.get(code=STATUS_PAYMENT_SUCCESS)
            self.order.save()
            return True
        #self.order.status = StatusCommon.objects.get(code=STATUS_CANCELED)
        self.order.save()
        return False
