from django.shortcuts import render
from dbApp.models import *
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers

# Create your views here.

def asset_total(request):
    asset_total_list = Asset.objects.all()
    context = {'asset_total_list': asset_total_list}
    return render(request, 'dbApp/asset_total.html', context)

def server_asset(request):
    server_asset_list = Server.objects.all()
    temp_list = []
    for server in server_asset_list:
        temp_dict = {}
        temp_dict['assetnum']=server.assetInfo.assetNum
        temp_dict['managenum']=server.manageNum
        temp_dict['managespec']=server.manageSpec
        temp_dict['core']=server.core
        temp_dict['ip']=server.ip
        temp_location = server.serverlocation
        if temp_location.rack_pk is not None:
            temp_dict['location']=temp_location.rack_pk.location
        else:
            temp_dict['location']=temp_location.realLocation
        temp_dict['onoff']= True
        temp_list.append(temp_dict)
    context = {'server_asset_list': temp_list}
    return render(request, 'dbApp/server_asset.html', context)
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
