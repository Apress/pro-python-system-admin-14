from ip_addresses.models import NetworkAddress
from django.contrib import admin

class NetworkAddressAdmin(admin.ModelAdmin):
    pass

admin.site.register(NetworkAddress, NetworkAddressAdmin)

