from htpayway.views import begin, failure, success
try:
    from django.conf.urls.defaults import patterns, url
except ImportError:
    from django.conf.urls import patterns, url


urlpatterns = patterns(
    '',
    url(r'^begin/(?P<transaction_id>\d+)/$', begin, name='htpayway_begin'),
    url(r'^success/$', success, name='htpayway_success'),
    url(r'^failure/$', failure, name='htpayway_failure'),
)
