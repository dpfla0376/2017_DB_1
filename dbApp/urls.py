from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.service_resources, name='service_resources'),
    url(r'asset$', views.asset_total, name='asset_total'),
]