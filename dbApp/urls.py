from django.conf.urls import url
from dbApp import views

urlpatterns = [
    url(r'^$', views.welcome, name='welcome_page'),
    url(r'^sign_in/$', views.sign_in, name='sign_in'),
    url(r'^sign_up/$', views.SignUp.as_view(), name='sign_up'),

    url(r'^rack/$', views.rack_asset, name='rack_asset'),
    url(r'^rack/total/$', views.rack_info, name='rack_info'),
    url(r'^rack/detail/$', views.rack_detail, name='rack_detail'),

    url(r'^asset/$', views.asset_total, name='asset_total'),

    url(r'^asset/edit/([0-9]+)$', views.edit_asset, name='edit_asset'),
    url(r'^asset/delete/([0-9]+)/$', views.delete_asset, name='delete_asset'),
    url(r'^asset/detail/$', views.asset_detail, name='asset_detail'),

    url(r'^server/$', views.server_asset, name='server_asset'),
    url(r'^server/detail/$', views.server_detail, name='server_detail'),

    url(r'^(?P<asset_type>[\w]+)/delete/(?P<manage_num>[\w]+)/$', views.delete_one_asset, name='delete_one_asset'),
    url(r'^(?P<asset_type>[\w]+)/edit/(?P<manage_num>[\w]+)/$', views.edit_one_asset, name='edit_one_asset'),
    url(r'^(?P<asset_type>[\w]+)/save/(?P<id>[\w]+)/$', views.save_one_asset, name='save_one_asset'),
    url(r'^(?P<asset_type>[\w]+)/location/(?P<manage_num>[\w]+)/$', views.get_location, name='get_location'),

    url(r'^switch/$', views.switch_asset, name='switch_asset'),
    url(r'^switch/detail/$', views.switch_detail, name='switch_detail'),

    url(r'^storage/$', views.storage_asset, name='storage_asset'),
    url(r'^storage/total$', views.storage_total, name='storage_total'),
    url(r'^storage/service$', views.service_storage, name='service_storage'),

    url(r'^resource/$', views.service_resources, name='service_resources'),
    url(r'^resource/storage/$', views.service_detail, name='service_detail'),
    url(r'^resource/service/(\d+)/$', views.service_detail, name='service_detail'),
    url(r'^resource/service/$', views.storage_use, name='storage_use'),
    url(r'^api/graph/total/storage/$', views.api_graph_storage_total, name='api_graph_storage_total'),
    url(r'^api/graph/service/$', views.api_graph_service_info, name='api_graph_service_info'),

    url(r'^add/$', views.add, name='add'),
    url(r'^add/(?P<add_type>[\w]+)/$', views.add, name='add'),

    url(r'^search/$', views.search_assets, name='search'),
]
