from django.conf.urls import patterns, url, include
#from django.views.generic import list_detail, create_update
from models import *
import views
from django.core.urlresolvers import reverse

classrule_info = {
    'queryset': ClassRule.objects.all(),
    'template_name': 'display_classrule.html',
}

classrule_form = {
    'form_class': ClassRuleForm,
    'template_name': 'add.html',
}

classrule_delete = {
    'model': ClassRule,
    'post_delete_redirect': '../..',
    'template_name': 'delete_confirm_classrule.html',
}

urlpatterns = patterns('',
    url(r'^networkaddress/$', views.networkaddress_display, name='networkaddress_displaytop'),
    url(r'^networkaddress/add/$', views.networkaddress_add, name='networkaddress_addtop'),
    url(r'^networkaddress/(?P<address>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})/$', views.networkaddress_display, name='networkaddress_display'),
    url(r'^networkaddress/(?P<address>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})/delete/$', views.networkaddress_delete, name='networkaddress_delete'),
    url(r'^networkaddress/(?P<address>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})/add/$', views.networkaddress_add, name='networkaddress_add'),
    url(r'^networkaddress/(?P<address>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})/modify/$', views.networkaddress_modify, name='networkaddress_modify'),
    url(r'^networkaddress/(?P<address>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})/add_dhcp/$', views.dhcpnetwork_add, name='networkaddress_adddhcp'),
    url(r'^networkaddress/(?P<address>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/ping/$', views.networkaddress_ping, name='networkaddress_ping'),
    url(r'^networkaddress/$', views.networkaddress_ping, name='networkaddress_ping_url'),

    url(r'^dhcpnetwork/(?P<address>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})/$', views.dhcpnetwork_display, name='dhcpnetwork-display'),
    url(r'^dhcpnetwork/(?P<address>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})/delete/$', views.dhcpnetwork_delete, name='dhcpnetwork-delete'),
    url(r'^dhcpnetwork/(?P<address>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})/modify/$', views.dhcpnetwork_modify, name='dhcpnetwork-modify'),
    url(r'^dhcpnetwork/(?P<address>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})/add_dhcppool/$', views.dhcpaddresspool_add, name='dhcpnetwork-addpool'),

    url(r'^dhcpaddresspool/add/$', views.dhcpaddresspool_add),
    url(r'^dhcpaddresspool/(?P<range_start>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/(?P<range_finish>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/$', views.dhcpaddresspool_display, name='dhcpaddresspool-display'),
    url(r'^dhcpaddresspool/(?P<range>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/delete/$', views.dhcpaddresspool_delete, name='dhcpaddresspool-delete'),

    url(r'^classrule/$', views.ClassRuleDisplay.as_view(), name='classrule_displaytop'),
    url(r'^classrule/(?P<pk>\d+)/$', views.ClassRuleDetailDisplay.as_view(), name='classrule_display'),
    url(r'^classrule/(?P<pk>\d+)/modify/$', views.ClassRuleUpdate.as_view(), name='classrule_modify'),
    url(r'^classrule/(?P<pk>\d+)/delete/$', views.ClassRuleDelete.as_view(), name='classrule_delete'),
    url(r'^classrule/add/$', views.ClassRuleCreate.as_view(), name='classrule_add'),

    url(r'^dhcpd.conf/$', views.dhcpd_conf_generate, name='dhcp_conf_generate'),
)

