from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.welcome, name='welcome_page'),
    url(r'asset/$', views.asset_total, name='asset_total'),
    url(r'server/$', views.server_asset, name='server_asset'),
    url(r'switch/$', views.switch_asset, name='switch_asset'),
    url(r'service_detail/$', views.service_detail, name='service_detail'),
    url(r'resource/$', views.service_resources, name='service_resources'),
    url(r'aaaa/$', views.SignUp.as_view(), name='sign_up'),
    url(r'sign_up/$', views.SignUp.as_view(), name='sign_up'),
    url(r'add/$', views.add, name='add'),

]