from django.shortcuts import render
from dbApp.models import *
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import time

# Create your views here.

def asset_total(request):
    asset_total_list = Asset.objects.all()
    context = {'asset_total_list': asset_total_list}
    return render(request, 'dbApp/asset_total.html', context)

def switch_asset(request):
    switch_asset_list = Switch.objects.select_related('location','assetInfo','location__rack').all()
    temp_list = []
    for switch in switch_asset_list:
        temp_dict = {}
        temp_dict['assetNum']=switch.assetInfo.assetNum
        temp_dict['manageNum']=switch.manageNum
        temp_dict['manageSpec']=switch.manageSpec
        temp_dict['ip']=switch.ip
        temp_location = switch.location
        if temp_location.rack is not None:
            temp_dict['location']=temp_location.rack.location
        else:
            temp_dict['location']=temp_location.realLocation
        temp_dict['onOff']=True
        temp_list.append(temp_dict)
    context = {'switch_asset_list': temp_list}
    return render(request, 'dbApp/switch_asset.html', context)

def server_asset(request):
    start_time = time.time()
    server_asset_list = Server.objects.select_related('location','assetInfo','location__rack_pk').all()
    temp_list = list()
    for server in server_asset_list:
        temp_dict = dict()
        temp_dict['assetnum']=server.assetInfo.assetNum
        temp_dict['managenum']=server.manageNum
        temp_dict['managespec']=server.manageSpec
        temp_dict['core']=server.core
        temp_dict['ip']=server.ip
        temp_location = server.location
        if temp_location.rack_pk is not None:
            temp_dict['location']=temp_location.rack_pk.location
        else:
            temp_dict['location']=temp_location.realLocation
        temp_dict['onoff']= True
        temp_list.append(temp_dict)
    context = {'server_asset_list': temp_list}
    temppp = render(request, 'dbApp/server_asset.html', context)
    print("--- %s seconds ---" % (time.time() - start_time))
    return temppp
    # return HttpResponse(temp_list)

def service_resources(request):
    return render(request, 'dbApp/service_resources.html', {});

def service_detail(request):
    server_list = ServerService.objects.all()
    storage_list = StorageService.objects.all()
    data = json.loads(request.POST.get('data'))
    server_service_list = ServerService.objects.get(service=data[???])
    storage_storage_list = StorageService.objects.get(service=data[???])
    return render(request, 'dpApp/service_detail.html', {});

def insert_asset(request):
    asset_total_list = Asset.objects.all()
    context = {'asset_total_list': asset_total_list}
    return render(request, 'dbApp/asset_total.html', context)


def sign_up(request):
    return render(request, 'dbApp/resistration.html')
