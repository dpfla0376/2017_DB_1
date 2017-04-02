from django.contrib import admin
from dbApp.models import Asset, Service, StorageAsset

# Register your models here.
admin.site.register(Asset)
admin.site.register(Service)
admin.site.register(StorageAsset)