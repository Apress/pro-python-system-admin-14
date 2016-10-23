from django.contrib import admin
from httpconfig.models import *


class VHostDirectiveInLine(admin.TabularInline):
    model = VHostDirective
    extra = 1

class VirtualHostAdmin(admin.ModelAdmin):
    inlines = (VHostDirectiveInLine,)
    list_display = ('description', 'is_default', 'is_template', 
                    'bind_address', 'domain_names', 'code_snippet')

    actions = ('make_default', 'duplicate',)

    def make_default(self, request, queryset):
        if len(queryset) == 1:
            VirtualHost.objects.all().update(is_default=False)
            queryset.update(is_default=True)
            self.message_user(request, 
                 "Virtual host '%s' has been made the default virtual host" % queryset[0])
        else:
            self.message_user(request, 'ERROR: Only one host can be set as the default!')
    make_default.short_description = 'Make selected Virtual Host default'

    def duplicate(self, request, queryset):
        msg = ''
        for vhost in queryset:
            new_vhost = VirtualHost()
            new_vhost.description = "%s (Copy)" % vhost.description
            new_vhost.bind_address = vhost.bind_address
            new_vhost.is_template = False
            new_vhost.is_default = False
            new_vhost.save()
            # recreate all 'orphan' directives that aren't parents
            o=vhost.vhostdirective_set.filter(parent=None).filter(directive__is_container=False)
            for vhd in o:
                new_vhd = VHostDirective()
                new_vhd.directive = vhd.directive
                new_vhd.value = vhd.value
                new_vhd.vhost = new_vhost
                new_vhd.save()
            # recreate all parent directives
            for vhd in vhost.vhostdirective_set.filter(directive__is_container=True):
                new_vhd = VHostDirective()
                new_vhd.directive = vhd.directive
                new_vhd.value = vhd.value
                new_vhd.vhost = new_vhost
                new_vhd.save()
                # and all their children
                for child_vhd in vhost.vhostdirective_set.filter(parent=vhd):
                    msg += str(child_vhd)
                    new_child_vhd = VHostDirective()
                    new_child_vhd.directive = child_vhd.directive
                    new_child_vhd.value = child_vhd.value
                    new_child_vhd.vhost = new_vhost
                    new_child_vhd.parent = new_vhd
                    new_child_vhd.save()
        self.message_user(request, msg)
    duplicate.short_description = 'Duplicate selected Virtual Hosts'



class VHostDirectiveAdmin(admin.ModelAdmin):
    pass

class ConfigDirectiveAdmin(admin.ModelAdmin):
    fieldsets = [
                    (None,      {'fields': ['name']}),
                    ('Details', {'fields': ['is_container', 'documentation'],
                             'classes': ['collapse'],
                             'description': 'Specify the config directive details'})
                ]



admin.site.register(VirtualHost, VirtualHostAdmin)
admin.site.register(ConfigDirective, ConfigDirectiveAdmin)
admin.site.register(VHostDirective, VHostDirectiveAdmin)

