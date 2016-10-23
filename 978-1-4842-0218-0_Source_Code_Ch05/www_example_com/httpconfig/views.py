from httpconfig.models import *
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404

# Create your views here.

def full_config(request, object_id=None):
    if not object_id:
        vhosts = VirtualHost.objects.all()
    else:
        vhosts = VirtualHost.objects.filter(id=object_id)
    vhosts_list = []
    for vhost in vhosts:
        vhost_struct = {}
        vhost_struct['vhost_data'] = vhost
        vhost_struct['orphan_directives'] = \
          vhost.vhostdirective_set.filter(directive__is_container=False).filter(parent=None)
        vhost_struct['containers'] = []
        for container_directive in \
          vhost.vhostdirective_set.filter(directive__is_container=True):
            vhost_struct['containers'].append({'parent': container_directive,
                                               'children': \
          vhost.vhostdirective_set.filter(parent=container_directive),
                                              })
        vhosts_list.append(vhost_struct)
    return render_to_response('full_config.txt', 
                              {'vhosts': vhosts_list},
                              mimetype='text/plain')

