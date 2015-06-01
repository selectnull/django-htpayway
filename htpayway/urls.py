from django.conf.urls.defaults import patterns, url
from htpayway.views import create, failure, success


urlpatterns = patterns(
    '',
    url(r'^create/$', create, name='htpayway_create'),
    url(r'^success/$', success, name='htpayway_success'),
    url(r'^failure/$', failure, name='htpayway_failure'),
)
