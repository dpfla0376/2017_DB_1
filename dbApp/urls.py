from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.asset_total, name='asset_total'),
    url(r'asset$', views.asset_total, name='asset_total'),
    url(r'server$', views.server_asset, name='server_asset'),
]