from django.conf.urls import patterns, include, url

urlpatterns = patterns('httpconfig.views',
    url(r'^$', 'full_config'),
    url(r'^(?P<object_id>\d+)/$', 'full_config'),
)

