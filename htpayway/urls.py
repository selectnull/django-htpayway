from htpayway.views import create, failure, success
try:
    from django.conf.urls.defaults import patterns, url
except ImportError:
    from django.conf.urls import patterns, url


urlpatterns = patterns(
    '',
    url(r'^create/$', create, name='htpayway_create'),
    url(r'^success/$', success, name='htpayway_success'),
    url(r'^failure/$', failure, name='htpayway_failure'),
)
