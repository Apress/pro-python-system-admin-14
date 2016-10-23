from django.conf.urls import patterns, include, url

urlpatterns = patterns('ip_addresses.views',
    url(r'^networkaddress/$', 'display'),
    url(r'^networkaddress/(?P<address>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})/$', 'display'),
    url(r'^networkaddress/(?P<address>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})/delete/$', 'delete'),
    url(r'^networkaddress/(?P<address>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})/add/$', 'add'),
    url(r'^networkaddress/add/$', 'add'),
    url(r'^networkaddress/(?P<address>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})/modify/$', 'modify'),
    url(r'^networkaddress/modify/$', 'modify'),
)

