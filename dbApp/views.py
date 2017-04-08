from django.shortcuts import render
from dbApp.models import *

from django.views.generic import View
import json
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
import time

# Create your views here.

# Private Methods
def dictFetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

# API
def api_graph_storage_total(request):
    cursor = connection.cursor()
    cursor.execute('SELECT sa.storageForm as name, SUM(ss.allocSize) as size FROM `dbApp_storageasset` sa ' +
        'INNER JOIN `dbApp_storage` s ON s.storageAsset_id = sa.id ' +
        'INNER JOIN `dbApp_storageservice` ss ON ss.storage_id = s.id ' +
        'group by sa.storageForm')
    usage_sum_list = dictFetchall(cursor)

    cursor.execute('SELECT sa.storageForm as name, SUM(s.Vol) as size FROM `dbApp_storageasset` sa ' +
        'INNER JOIN `dbApp_storage` s ON s.storageAsset_id = sa.id ' +
        'group by sa.storageForm')
    total_sum_list = dictFetchall(cursor)

    return HttpResponse(json.dumps({ 'total': total_sum_list, 'usage': usage_sum_list }))

def api_graph_service_info(request):
    service_list = []
    for service in Service.objects.all():
        temp_dict = {}
        temp_dict['id'] = service.id
        temp_dict['name'] = service.serviceName
        service_list.append(temp_dict)

    cursor = connection.cursor()
    cursor.execute('SELECT sv.id, ss.Use, SUM(core) AS core ' +
                   'FROM `dbApp_service` sv ' +
                   'INNER JOIN `dbApp_serverservice` ss on ss.service_id = sv.id ' +
                   'INNER JOIN `dbApp_server` sr on sr.id = ss.server_id ' +
                   'GROUP BY sv.id, ss.Use')
    service_core_info_data = dictFetchall(cursor)

    service_core_info = []
    for core in service_core_info_data:
        core_info = {}
        core_info['id'] = core.get('id')
        core_info['use'] = core.get('Use')
        core_info['core'] = int(core.get('core'))
        service_core_info.append(core_info)

    cursor.execute('SELECT sv.id, sa.storageForm AS type, SUM(ss.allocSize) as size ' +
                   'FROM `dbApp_service` sv ' +
                   'INNER JOIN `dbApp_storageservice` ss ON ss.service_id = sv.id ' +
                   'INNER JOIN `dbApp_storage` st ON st.id = ss.storage_id ' +
                   'INNER JOIN `dbApp_storageasset` sa ON sa.id = st.storageAsset_id ' +
                   'GROUP BY sv.id, sa.storageForm')
    service_storage_info = dictFetchall(cursor)

    return HttpResponse(json.dumps({ 'list': service_list, 'core': service_core_info, 'storage': service_storage_info }))

# Logic

def asset_total(request):
    asset_total_list = Asset.objects.all()
    context = {'asset_total_list': asset_total_list}
    return render(request, 'dbApp/asset_total.html', context)


def switch_asset(request):
    switch_asset_list = Switch.objects.all()
    temp_list = []
    for switch in switch_asset_list:
        temp_dict = {}
        temp_dict['assetNum']=switch.assetInfo.assetNum
        temp_dict['manageNum']=switch.manageNum
        temp_dict['manageSpec']=switch.manageSpec
        temp_dict['ip']=switch.ip
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
    service_list = Service.objects.all()
    temp_list = []
    for service in service_list:
        temp_dict = {}
        temp_dict['id'] = service.id
        temp_dict['name'] = service.serviceName
        temp_list.append(temp_dict)
    context = {'service_list': temp_list}
    return render(request, 'dbApp/service_resources.html', context)


def service_detail(request):
    #server_list = ServerService.objects.all()
    #storage_list = StorageService.objects.all()
    #data = json.loads(request.POST.get('data'))
    #server_service_list = ServerService.objects.get(service=data[???])
    #storage_service_list = StorageService.objects.get(service=data[???])
    #context = {'server_service_list': server_service_list, 'storage_service_list' : storage_service_list}
    return render(request, 'dbApp/service_detail.html', {});


def insert_asset(request):
    asset_total_list = Asset.objects.all()
    context = {'asset_total_list': asset_total_list}
    return render(request, 'dbApp/asset_total.html', context)


def sign_in(request):
    data = request.POST
    username = data['inputUserName']
    password = data['inputPassword']
    print(username)
    print(password)
    return render(request, 'dbApp/service_resources.html')


def welcome(request):
    return render(request, 'dbApp/welcome_page.html', {})


class SignUp(View):
    def get(self, request):
        return render(request, 'dbApp/resistration.html')

    def post(self, request):
        print(request.POST)
        return HttpResponse("request.POST")


def add(request, add_type):
    if request.method == "POST":
        if add_type == "asset":
            new_asset = Asset()
            new_asset.assetNum = 2016
            new_asset.acquisitionDate = request.POST.get("")
            new_asset.assetName = models.CharField(max_length=45)
            new_asset.standard = models.CharField(max_length=45)
            new_asset.acquisitionCost = models.IntegerField()
            new_asset.purchaseLocation = models.CharField(max_length=45)
            new_asset.maintenanceYear = models.IntegerField()
            #a.save()
            return HttpResponse("ASSET")
        elif add_type == "service":
            temp_service = Service.objects.create(serviceName=request.POST.get("service_name"), makeDate=request.POST.get("service_make_date"), color=request.POST.get("service_color"))
            #
            # tempService = Service.objects.get(id=1)
            # tempService.serviceName = request.POST.get("service_name")
            # tempService.makeDate = request.POST.get("service_make_date")
            # tempService.color = request.POST.get("service_color")
            # tempService.save()

            # new_service.save()
            print("<"+temp_service.serviceName+">")
            print("<"+temp_service.makeDate+">")
            print("<"+temp_service.color+">")
            return HttpResponse("SERVICE")
    else:
        if add_type == "asset":
            return render(request, 'dbApp/add_asset.html')
        elif add_type == "service":
            return render(request, 'dbApp/add_service.html')
