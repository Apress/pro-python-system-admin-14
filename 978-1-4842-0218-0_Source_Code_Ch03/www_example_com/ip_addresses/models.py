from django.db import models
from django.forms import ModelForm

class NetworkAddress(models.Model):
    address = models.IPAddressField()
    network_size = models.PositiveIntegerField()
    description = models.CharField(max_length=400)
    parent = models.ForeignKey('self', blank=True, null=True)

class NetworkAddressAddForm(ModelForm):
    class Meta:
        model = NetworkAddress
        exclude = ('parent', )

class NetworkAddressModifyForm(ModelForm):
    class Meta:
        model = NetworkAddress
        fields = ('description',)

