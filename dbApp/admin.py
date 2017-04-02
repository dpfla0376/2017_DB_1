from django.contrib import admin
from dbApp.models import Asset, Service, StorageAsset, Server

# Register your models here.
admin.site.register(Asset)
admin.site.register(Service)
admin.site.register(StorageAsset)
admin.site.register(Server)