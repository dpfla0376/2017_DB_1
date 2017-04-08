import json
import time

from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View

from dbApp.models import *
from django.views.generic import View
import json
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.contrib.auth import authenticate
import time
from datetime import datetime

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

    return HttpResponse(json.dumps({'list': service_list, 'core': service_core_info, 'storage': service_storage_info}))


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
        temp_dict['assetNum'] = switch.assetInfo.assetNum
        temp_dict['manageNum'] = switch.manageNum
        temp_dict['manageSpec'] = switch.manageSpec
        temp_dict['ip'] = switch.ip
        temp_dict['onOff'] = True
        temp_list.append(temp_dict)
    context = {'switch_asset_list': temp_list}
    return render(request, 'dbApp/switch_asset.html', context)


def server_asset(request):
    start_time = time.time()
    server_asset_list = Server.objects.select_related('location', 'assetInfo', 'location__rack_pk').all()
    temp_list = list()
    for server in server_asset_list:
        temp_dict = dict()
        temp_dict['assetnum'] = server.assetInfo.assetNum
        temp_dict['managenum'] = server.manageNum
        temp_dict['managespec'] = server.manageSpec
        temp_dict['core'] = server.core
        temp_dict['ip'] = server.ip
        temp_location = server.location
        if temp_location.rack_pk is not None:
            temp_dict['location'] = temp_location.rack_pk.location
        else:
            temp_dict['location'] = temp_location.realLocation
        temp_dict['onoff'] = True
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
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM `dbApp_asset`INNER JOIN `dbApp_server` '
    + 'ON dbApp_asset.id = dbApp_server.assetInfo_id')
    server_list = dictFetchall(cursor)
    cursor.execute('SELECT * FROM `dbApp_storage` ' +
                   'INNER JOIN `dbApp_storageasset` ON dbApp_storageasset.id = dbApp_storage.storageAsset_id '+
                   'INNER JOIN `dbApp_storageservice` ON dbApp_storageservice.storage_id = dbApp_storage.id '+
                   'where dbApp_storageasset.storageForm = \'SAN\' ' )
    disk_SAN = dictFetchall(cursor)
    cursor.execute('SELECT * FROM `dbApp_storage` ' +
                   'INNER JOIN `dbApp_storageasset` ON dbApp_storageasset.id = dbApp_storage.storageAsset_id '+
                   'INNER JOIN `dbApp_storageservice` ON dbApp_storageservice.storage_id = dbApp_storage.id '+
                   'where dbApp_storageasset.storageForm = \'NAS\' ' )
    disk_NAS = dictFetchall(cursor)
    cursor.execute('SELECT * FROM `dbApp_storage` ' +
                   'INNER JOIN `dbApp_storageasset` ON dbApp_storageasset.id = dbApp_storage.storageAsset_id '+
                   'INNER JOIN `dbApp_storageservice` ON dbApp_storageservice.storage_id = dbApp_storage.id '+
                   'where dbApp_storageasset.storageForm = \'TAPE\' ' )
    disk_TAPE = dictFetchall(cursor)

    return render(request, 'dbApp/service_detail.html', {});

def storage_use(request):
    #server_list = ServerService.objects.all()
    #storage_list = StorageService.objects.all()
    #data = json.loads(request.POST.get('data'))
    #server_service_list = ServerService.objects.get(service=data[???])
    #storage_service_list = StorageService.objects.get(service=data[???])
    #context = {'server_service_list': server_service_list, 'storage_service_list' : storage_service_list}
    return render(request, 'dbApp/storage_use.html', {});

def rack_info(request):
    rack_total = list(Rack.objects.values('manageNum'))
    rack_list = {}
    rack_name = {}
    for rack in rack_total:
        temp = rack['manageNum']    # ex) R11001
        temp_name = Rack.objects.get(manageNum=temp).location[-3:]  # ex) C03
        rack_list[rack['manageNum']] = []
        rack_name[temp_name] = rack['manageNum']
    print(rack_list)
    print(rack_name)

    server_asset_list = Server.objects.select_related('location', 'location__rack_pk').all()
    switch_asset_list = Switch.objects.select_related('location', 'location__rack').all()
    # make server list for rack
    for server in server_asset_list:
        temp_subDict = dict()
        temp_subDict['manageNum'] = server.manageNum
        temp_subDict['manageSpec'] = server.manageSpec
        temp_subDict['ip'] = server.ip
        temp_subDict['size'] = server.size
        temp_service = ServerService.objects.get(server=server)
        temp_subDict['serviceName'] = temp_service.service.serviceName
        temp_subDict['use'] = temp_service.Use

        temp_location = server.location
        if temp_location.rack_pk is not None:
            temp_subDict['rack_pk'] = temp_location.rack_pk.manageNum
            temp_subDict['rackLocation'] = temp_location.rackLocation
        #print(temp_subDict)
        rack_list[temp_subDict['rack_pk']].append(temp_subDict)
        #print(rack_list)

    # make server list for rack
    for switch in switch_asset_list:
        temp_subDict = dict()
        temp_subDict['manageNum'] = switch.manageNum
        temp_subDict['manageSpec'] = switch.manageSpec
        temp_subDict['ip'] = switch.ip
        temp_subDict['use'] = switch.serviceOn

        temp_location = switch.location
        if temp_location.rack is not None:
            temp_subDict['rack_pk'] = temp_location.rack.manageNum
            temp_subDict['rackLocation'] = temp_location.rackLocation
        print(temp_subDict)
        rack_list[temp_subDict['rack_pk']].append(temp_subDict)
        print(rack_list)

    rack_total = []
    for rack in rack_name:
        temp = {}
        temp['id'] = rack_name[rack]
        temp['list'] = sorted(rack_list[temp['id']], key=lambda k: k['rackLocation'], reverse=True)
        temp['name'] = rack
        rack_total.append(temp)


    print(list(rack_list.keys()))
    print(rack_total)
    context = {'rack_list': rack_total, 'loop_times' : range(42, 0, -1)}
    return render(request, 'dbApp/rack_info.html', context)

def sub42(value):
    return 42 - value

def insert_asset(request):
    asset_total_list = Asset.objects.all()
    context = {'asset_total_list': asset_total_list}
    return render(request, 'dbApp/asset_total.html', context)

def sign_in(request):
    data = request.POST
    email = data['email']
    password = data['password']
    user = authenticate(username=email, password=password)
    if user is None:
        context = {'messages': 'login failed'}
        return render(request, 'dbApp/welcome_page.html',context)
    # return service_resources(request)
    return HttpResponseRedirect('/dbApp/resource/')


def welcome(request):
    return render(request, 'dbApp/welcome_page.html', {})


class SignUp(View):
    def get(self, request):
        return render(request, 'dbApp/resistration.html')
    def post(self, request):
        data = request.POST
        name = data['name']
        password = data['password']
        email = data['email']
        user = User.objects.create_user(username = email,email = email,password=password)
        user.first_name = name
        return welcome(request)


def add(request, add_type):
    if request.method == "POST":
        if add_type == "asset":
            # add asset
            acq_year = str(request.POST.get("acquisition_date"))[0:4]
            temp_asset = Asset.objects.filter(assetNum__startswith=acq_year).order_by('-assetNum').first()

            if temp_asset:
                this_asset_num = str(int(temp_asset.assetNum) + 1)
            else:
                this_asset_num = int(str(request.POST.get("acquisition_date"))[0:4])*1000000+1

            new_asset = Asset.objects.create(assetNum=this_asset_num,
                                             acquisitionDate=request.POST.get("acquisition_date"),
                                             assetName=request.POST.get("asset_name"),
                                             standard=request.POST.get("standard"),
                                             acquisitionCost=request.POST.get("acquisition_cost"),
                                             purchaseLocation=request.POST.get("acquisition_location"),
                                             maintenanceYear=request.POST.get("maintenance_year"))
            add_servers(request, new_asset)
            #add_switches(request, new_asset)
            #add_racks(request, new_asset)

            return HttpResponse("ASSET")

        elif add_type == "service":

            hex_color = request.POST.get("service_color").lstrip('#')
            rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

            temp_service = Service.objects.create(serviceName=request.POST.get("service_name"),
                                                  makeDate=request.POST.get("service_make_date"),
                                                  color=request.POST.get("service_color"))

            print("<" + temp_service.serviceName + ">")
            print("<" + temp_service.makeDate + ">")
            print("<" + temp_service.color + ">")
            return HttpResponse("SERVICE")
    else:
        if add_type == "asset":
            return render(request, 'dbApp/add_asset.html')
        elif add_type == "service":
            return render(request, 'dbApp/add_service.html')


def add_servers(request, new_asset):
    # add servers
    server_number = request.POST.get("server_number")
    temp_server = Server.objects.filter(manageNum__startswith="S" + str(new_asset.acquisitionDate)[2:4]).order_by(
        '-manageNum').first()
    if temp_server:
        this_server_manage_num = int(temp_server.manageNum[1:]) + 1
    else:
        this_server_manage_num = int(str(new_asset.acquisitionDate)[2:4])*1000+1
    for i in range(0, int(server_number)):
        new_server = Server.objects.create(manageNum="S"+str(this_server_manage_num),
                                           assetInfo=new_asset,
                                           manageSpec=new_asset.assetName,
                                           isInRack=False,
                                           size=request.POST.get("server_size"),
                                           core=request.POST.get("server_core_num"),
                                           ip="127.0.0.1")
        this_server_manage_num += 1

        ServerLocation.objects.create(
            server_pk=new_server,
            rack_pk=None,
            rackLocation=None,
            realLocation=request.POST.get('server_location'))


def add_switches(request, new_asset):
    # add switches
    switch_number = request.POST.get("switch_number")
    temp_switch = Service.objects.filter(manageNum__startswith="N" + str(new_asset.acquisitionDate)[2:4]).order_by(
        '-manageNum').first()
    if temp_switch:
        this_switch_manage_num = int(temp_switch.manageNum[1:]) + 1
    else:
        this_switch_manage_num = int(str(datetime.now().year)[2:]) * 1000 + 1
    for i in range(0, switch_number):
        new_switch = Switch.objects.create(manageNum="N"+str(this_switch_manage_num),
                                           assetInfo=new_asset,
                                           manageSpec=new_asset.assetName,
                                           isInRack=False,
                                           size=request.POST.get("switch_size"),
                                           serviceOn=False,
                                           ip="127.0.0.1")
        this_switch_manage_num += 1

        SwitchLocation.objects.create(
            switch_pk=new_switch,
            rack_pk=None,
            rackLocation=None,
            realLocation=request.POST.get('switch_location'))


def add_racks(request, new_asset):
    # add racks
    rack_number = request.POST.get("rack_number")
    temp_rack = Rack.objects.filter(manageNum__startswith="R" + str(new_asset.acquisitionDate)[2:4]).order_by(
        '-manageNum').first()
    if temp_rack:
        this_rack_manage_num = int(temp_rack.manageNum[1:]) + 1
    else:
        this_rack_manage_num = int(str(new_asset.acquisitionDate)[2:4]) * 1000 + 1

    for i in range(0, rack_number):
        new_rack = Rack.objects.create(manageNum="R"+str(this_rack_manage_num),
                                       assetInfo=new_asset,
                                       manageSpec=new_asset.assetName,
                                       size=request.POST.get("rack_size"),
                                       location=request.POST.get("rack_location"))
        this_rack_manage_num += 1



