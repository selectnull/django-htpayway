from django.conf.urls.defaults import patterns, url
from htpayway.views import transaction_create, transaction_failure,\
    transaction_success

urlpatterns = patterns(
    '',
    url(r'^create/$', transaction_create, name='transaction_create'),
    url(r'^success/$', transaction_success, name='transaction_success'),
    url(r'^failure/$', transaction_failure, name='transaction_failure'),
)
