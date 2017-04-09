from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.welcome, name='welcome_page'),
    url(r'^sign_in/$', views.sign_in, name='sign_in'),
    url(r'^sign_up/$', views.SignUp.as_view(), name='sign_up'),

    url(r'^rack/$', views.rack_asset, name='rack_asset'),
    url(r'^rack_total_view/$', views.rack_info, name='rack_info'),
    url(r'^rack/rack_detail/$', views.rack_detail, name='rack_detail'),

    url(r'^asset/$', views.asset_total, name='asset_total'),
    url(r'^asset/asset_detail/$', views.asset_detail, name='asset_detail'),
    url(r'^asset/edit_asset/$', views.edit_asset, name='edit_asset'),
    url(r'^asset/delete_asset/([0-9]+)/$', views.delete_asset, name='delete_asset'),

    url(r'^server/$', views.server_asset, name='server_asset'),
    url(r'^server/server_detail/$', views.server_detail, name='server_detail'),

    url(r'^switch/$', views.switch_asset, name='switch_asset'),
    url(r'^switch/switch_detail/$', views.switch_detail, name='switch_detail'),

    url(r'^resource/$', views.service_resources, name='service_resources'),
    url(r'^resource/storage_detail/$', views.service_detail, name='service_detail'),
    url(r'^resource/service_detail/$', views.service_detail, name='service_detail'),
    url(r'^api/graph/total/storage/$', views.api_graph_storage_total, name='api_graph_storage_total'),
    url(r'^api/graph/service/$', views.api_graph_service_info, name='api_graph_service_info'),

    url(r'^add/$', views.add, name='add'),
    url(r'^add/(?P<add_type>[\w]+)/$', views.add, name='add'),

    url(r'^search/$', views.search_assets, name='search'),
]
