from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.service_resources, name='service_resources'),
    url(r'asset$', views.asset_total, name='asset_total'),
    url(r'server$', views.server_asset, name='server_asset'),
    url(r'service_detail$', views.service_detail, name='service_detail'),
    url(r'aaaa$', views.sign_up, name='sign_up'),
]