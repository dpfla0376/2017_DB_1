# -*- coding: utf-8 -*-

from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.db.models import Q
from django.db.models import Prefetch
from dbApp.models import *
from datetime import datetime

import json, time, jwt


# import json, jwt, time
# Create your views here.

# Private Methods

def dictFetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def sub42(value):
    return 42 - value


def getUser(session):
    try:
        username = session['usertoken']
        return User.objects.get(username=username)
    except KeyError:
        return None


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

    return HttpResponse(json.dumps({'total': total_sum_list, 'usage': usage_sum_list}))


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

class SignUp(View):  # 회원가입
    def get(self, request):
        return render(request, 'dbApp/registration.html')

    def post(self, request):
        data = request.POST
        name = data['name']
        password = data['password']
        email = data['email']
        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = name
        return HttpResponseRedirect('/dbApp/')


def sign_in(request):
    data = request.POST
    email = data['email']
    password = data['password']
    user = authenticate(username=email, password=password)
    if user is None:
        context = {'messages': 'login failed'}
        return render(request, 'dbApp/welcome_page.html', context)
    request.session['usertoken'] = email
    return HttpResponseRedirect('/dbApp/resource/')


def welcome(request):
    return render(request, 'dbApp/welcome_page.html', {})


def asset_total(request):
    server_prefetch = Prefetch('server', to_attr='servers')
    switch_prefetch = Prefetch('switch', to_attr='switches')
    storage_prefetch = Prefetch('storageasset', to_attr='storages')
    rack_prefetch = Prefetch('rack', to_attr='racks')
    asset_total_list = Asset.objects.all().prefetch_related(server_prefetch, switch_prefetch, storage_prefetch,
                                                            rack_prefetch)
    temp_list = []
    for asset in asset_total_list:
        server_num = len(asset.servers)
        switch_num = len(asset.switches)
        storage_num = len(asset.storages)
        rack_num = len(asset.racks)
        temp_dict = dict()
        temp_dict['assetNum'] = asset.assetNum
        temp_dict['acquisitionDate'] = asset.acquisitionDate
        temp_dict['assetName'] = asset.assetName
        temp_dict['standard'] = asset.standard
        temp_dict['acquisitionCost'] = asset.acquisitionCost
        temp_dict['purchaseLocation'] = asset.purchaseLocation
        temp_dict['maintenanceYear'] = asset.maintenanceYear
        temp_dict['serverNum'] = server_num
        temp_dict['switchNum'] = switch_num
        temp_dict['storageNum'] = storage_num
        temp_dict['rackNum'] = rack_num
        temp_dict['totalNum'] = server_num + switch_num + storage_num + rack_num
        temp_list.append(temp_dict)
    context = {'asset_total_list': temp_list}
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
        temp_location = switch.location
        if temp_location.rack is not None:
            temp_dict['location'] = temp_location.rack.location
        else:
            temp_dict['location'] = temp_location.realLocation
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


# rack_asset 에 대한 페이지. Rack list 클릭하면 나옵니다.
def rack_asset(request):
    rack_asset_list = Rack.objects.all()
    temp_list = []
    for rack in rack_asset_list:
        temp_dict = {}
        temp_dict['assetNum'] = rack.assetInfo.assetNum
        temp_dict['manageNum'] = rack.manageNum
        temp_dict['manageSpec'] = rack.manageSpec
        temp_dict['size'] = rack.size
        temp_dict['location'] = rack.location
        temp_list.append(temp_dict)
    print(temp_list)
    context = {'rack_asset_list': temp_list}
    return render(request, 'dbApp/rack_asset.html', context)


def service_resources(request):  # 서비스의 리소스를 보여준다.
    # user = getUser(request.session) #여기부터 아래까지 총 3줄이 로그인 검증 부분입니당
    # if user is None:
    #    return HttpResponseRedirect('/dbApp/')
    service_list = Service.objects.all()
    temp_list = []
    for service in service_list:
        temp_dict = {}
        temp_dict['id'] = service.id
        temp_dict['name'] = service.serviceName
        temp_list.append(temp_dict)
    context = {'service_list': temp_list}
    return render(request, 'dbApp/service_resources.html', context)


def storage(request):
    cursor = connection.cursor()
    cursor.execute(
        'SELECT * FROM `dbApp_asset`INNER JOIN `dbApp_server` ON dbApp_asset.id = dbApp_server.assetInfo_id ' +
        'INNER JOIN `dbApp_serverlocation` ON dbApp_serverlocation.server_pk_id = dbApp_server.id ' +
        'INNER JOIN `dbApp_rack` ON dbApp_rack.id = dbApp_serverlocation.rack_pk_id ')
    server_list = dictFetchall(cursor)
    for server in server_list:
        if server['isInRack'] == 0:
            server['location'] = server['realLocation']
        if server['Use']:
            server['Use'] = True
        else:
            server['Use'] = False


def storage_asset(request):
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM `dbApp_asset` ' +
                   'INNER JOIN `dbApp_storageasset` ON dbApp_storageasset.assetInfo_id = dbApp_asset.id ')
    storage_list = dictFetchall(cursor)
    return render(request, 'dbApp/storage_asset.html', {'storage_list': storage_list});


def storage_detail(request):
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM `dbApp_asset` ' +
                   'INNER JOIN `dbApp_storageasset` ON dbApp_storageasset.assetInfo_id = dbApp_asset.id ' +
                   'INNER JOIN `dbApp_storage` ON dbApp_storageasset.id = dbApp_storage.storageAsset_id ' +
                   'INNER JOIN `dbApp_storageservice` ON dbApp_storageservice.storage_id = dbApp_storage.id ' +
                   'INNER JOIN  `dbApp_service` ON dbApp_service.id = dbApp_storageservice.service_id')
    storage_list = dictFetchall(cursor)
    return render(request, 'dbApp/storage_detail.html', {'storage_list': storage_list});


def service_storage(request):
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM `dbApp_asset` ' +
                   'INNER JOIN `dbApp_storageasset` ON dbApp_storageasset.assetInfo_id = dbApp_asset.id ' +
                   'INNER JOIN `dbApp_storage` ON dbApp_storageasset.id = dbApp_storage.storageAsset_id ' +
                   'INNER JOIN `dbApp_storageservice` ON dbApp_storageservice.storage_id = dbApp_storage.id ')
    storage_list = dictFetchall(cursor)

    cursor.execute('SELECT * FROM `dbApp_service` ')
    service_list = dictFetchall(cursor)
    return render(request, 'dbApp/storage_service.html', {'storage_list': storage_list,
                                                          'service_list': service_list});


def service_detail(request, pk):
    cursor = connection.cursor()
    cursor.execute(
        'SELECT * FROM `dbApp_asset`INNER JOIN `dbApp_server` ON dbApp_asset.id = dbApp_server.assetInfo_id ' +
        'INNER JOIN `dbApp_serverlocation` ON dbApp_serverlocation.server_pk_id = dbApp_server.id ' +
        'INNER JOIN `dbApp_rack` ON dbApp_rack.id = dbApp_serverlocation.rack_pk_id ' +
        'INNER JOIN dbApp_serverservice ON dbApp_serverservice.server_id = dbApp_server.id ' +
        'WHERE dbApp_serverservice.service_id = ' + pk)
    server_list = dictFetchall(cursor)
    for server in server_list:
        if server['isInRack'] == 0:
            server['location'] = server['realLocation']
        if server['Use']:
            server['Use'] = True
        else:
            server['Use'] = False

    cursor.execute('SELECT * FROM `dbApp_storage` ' +
                   'INNER JOIN `dbApp_storageasset` ON dbApp_storageasset.id = dbApp_storage.storageAsset_id ' +
                   'INNER JOIN `dbApp_storageservice` ON dbApp_storageservice.storage_id = dbApp_storage.id ' +
                   'where dbApp_storageasset.storageForm = \'SAN\' ' +
                   'and dbApp_storageservice.service_id = ' + pk)
    disk_SAN = dictFetchall(cursor)
    cursor.execute('SELECT * FROM `dbApp_storage` ' +
                   'INNER JOIN `dbApp_storageasset` ON dbApp_storageasset.id = dbApp_storage.storageAsset_id ' +
                   'INNER JOIN `dbApp_storageservice` ON dbApp_storageservice.storage_id = dbApp_storage.id ' +
                   'where dbApp_storageasset.storageForm = \'NAS\' ' +
                   'and dbApp_storageservice.service_id = ' + pk)
    disk_NAS = dictFetchall(cursor)
    cursor.execute('SELECT * FROM `dbApp_storage` ' +
                   'INNER JOIN `dbApp_storageasset` ON dbApp_storageasset.id = dbApp_storage.storageAsset_id ' +
                   'INNER JOIN `dbApp_storageservice` ON dbApp_storageservice.storage_id = dbApp_storage.id ' +
                   'where dbApp_storageasset.storageForm = \'TAPE\' ' +
                   'and dbApp_storageservice.service_id = ' + pk)
    disk_TAPE = dictFetchall(cursor)
    service = pk
    return render(request, 'dbApp/service_detail.html', {'service': service,
                                                         'server_asset_list': server_list,
                                                         'SAN': disk_SAN,
                                                         'NAS': disk_NAS,
                                                         'TAPE': disk_TAPE
                                                         });
''

def storage_use(request):
    # server_list = ServerService.objects.all()
    # storage_list = StorageService.objects.all()
    # data = json.loads(request.POST.get('data'))
    # server_service_list = ServerService.objects.get(service=data[???])
    # storage_service_list = StorageService.objects.get(service=data[???])
    # context = {'server_service_list': server_service_list, 'storage_service_list' : storage_service_list}
    return render(request, 'dbApp/storage_use.html', {});


# 엑셀의 rack_info 페이지. rack_total_view 를 보여줍니다.
def rack_info(request):
    start_time = time.time()
    rack_list = {}
    rack_name = {}

    rack_query_list = Rack.objects.all()
    for rack in rack_query_list:
        temp = rack.manageNum
        temp_name = rack.location[-3:]  # ex) C03
        rack_list[temp] = []
        rack_name[temp_name] = temp
    print(rack_list)
    print(rack_name)

    rack_query_list = Rack.objects.all()
    for rack in rack_query_list:
        temp = rack.manageNum
        temp_name = rack.location[-3:]  # ex) C03
        rack_list[temp] = []
        rack_name[temp_name] = temp
    my_prefetch = Prefetch('ss_server', queryset=ServerService.objects.select_related('service'), to_attr="services")
    # server_asset_list = Server.objects.select_related('location', 'location__rack_pk').all()
    # server_asset_list = Server.objects.select_related('location', 'location__rack_pk').all().prefetch_related(None)
    server_asset_list = Server.objects.select_related('location', 'location__rack_pk').prefetch_related(
        my_prefetch).all()

    switch_asset_list = Switch.objects.select_related('location', 'location__rack').all()
    # make server list for rack
    for server in server_asset_list:
        temp_subDict = dict()
        temp_subDict['manageNum'] = server.manageNum
        temp_subDict['manageSpec'] = server.manageSpec
        temp_subDict['ip'] = server.ip
        temp_subDict['size'] = server.size
        if len(server.services) is not 0:
            temp_serverservice = server.services[0]
            temp_subDict['use'] = temp_serverservice.Use
            temp_service = temp_serverservice.service
            temp_subDict['serviceName'] = temp_service.serviceName
            temp_subDict['color'] = temp_service.color
        temp_location = server.location
        if temp_location.rack_pk is not None:
            temp_subDict['rack_pk'] = temp_location.rack_pk.manageNum
            temp_subDict['rackLocation'] = temp_location.rackLocation
            rack_list[temp_subDict['rack_pk']].append(temp_subDict)
    # make server list for rack
    for switch in switch_asset_list:
        temp_subDict = dict()
        temp_subDict['manageNum'] = switch.manageNum
        temp_subDict['manageSpec'] = switch.manageSpec
        temp_subDict['ip'] = switch.ip
        temp_subDict['use'] = switch.serviceOn
        temp_subDict['size'] = switch.size
        temp_subDict['color'] = '255, 204, 255'

        temp_location = switch.location
        if temp_location.rack is not None:
            temp_subDict['rack_pk'] = temp_location.rack.manageNum
            temp_subDict['rackLocation'] = temp_location.rackLocation
            rack_list[temp_subDict['rack_pk']].append(temp_subDict)
    rack_total = []
    for rack in rack_name:
        temp = dict()
        temp['id'] = rack_name[rack]
        temp['list'] = sorted(rack_list[temp['id']], key=lambda k: k['rackLocation'], reverse=True)
        temp['name'] = rack
        rack_total.append(temp)
    data = []
    for rack in rack_total:
        position = [None] * 42
        for inrack in rack['list']:
            position[inrack["rackLocation"]] = inrack
        data.append({'data': list(reversed(position)), 'rack': rack})
    context = {'rack_list': rack_total, 'data': data}
    print("--- %s seconds ---" % (time.time() - start_time))
    return render(request, 'dbApp/rack_info.html', context)


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
    return service_resources(request)


def welcome(request):
    return render(request, 'dbApp/welcome_page.html', {})


class SignUp(View):
    def get(self, request):
        return render(request, 'dbApp/registration.html')
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
            print(request.POST.get("acquisition_date"))
            acq_year = str(request.POST.get("acquisition_date"))[0:4]
            temp_asset = Asset.objects.filter(assetNum__startswith=acq_year).order_by('-assetNum').first()

            if temp_asset:
                this_asset_num = str(int(temp_asset.assetNum) + 1)
            else:
                this_asset_num = int(str(request.POST.get("acquisition_date"))[0:4]) * 1000000 + 1

            new_asset = Asset.objects.create(assetNum=this_asset_num,
                                             acquisitionDate=request.POST.get("acquisition_date"),
                                             assetName=request.POST.get("asset_name"),
                                             standard=request.POST.get("standard"),
                                             acquisitionCost=request.POST.get("acquisition_cost"),
                                             purchaseLocation=request.POST.get("acquisition_location"),
                                             maintenanceYear=request.POST.get("maintenance_year"))
            if request.POST.get("server_button") == "on":
                add_servers(request, new_asset)

            if request.POST.get("switch_button") == "on":
                add_switches(request, new_asset)

            if request.POST.get("storage_button") == "on":
                add_storages(request, new_asset)

            if request.POST.get("rack_button") == "on":
                add_racks(request, new_asset)

            context = {'messages': '완료되었습니다.'}
            return render(request, 'dbApp/add_asset.html', context)

        elif add_type == "service":

            hex_color = request.POST.get("service_color").lstrip('#')
            rgb_tuple = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
            rgb = str(rgb_tuple[0]) + "," + str(rgb_tuple[1]) + "," + str(rgb_tuple[2])

            temp_service = Service.objects.create(serviceName=request.POST.get("service_name"),
                                                  makeDate=request.POST.get("service_make_date"),
                                                  color=rgb)
            context = {'messages': '완료되었습니다.'}
            return render(request, 'dbApp/add_service.html', context)
    else:
        if add_type == "asset":
            return render(request, 'dbApp/add_asset.html')
        elif add_type == "service":
            return render(request, 'dbApp/add_service.html')


def add_servers(request, new_asset):
    # add servers
    server_number = int(request.POST.get("server_number"))
    temp_server = Server.objects.filter(manageNum__startswith="S" + str(new_asset.acquisitionDate)[2:4]).order_by(
        '-manageNum').first()
    if temp_server:
        this_server_manage_num = int(temp_server.manageNum[1:]) + 1
    else:
        this_server_manage_num = int(str(new_asset.acquisitionDate)[2:4]) * 1000 + 1
    for i in range(0, int(server_number)):
        new_server = Server.objects.create(manageNum="S" + str(this_server_manage_num),
                                           assetInfo=new_asset,
                                           manageSpec=new_asset.assetName,
                                           isInRack=False,
                                           size=request.POST.get("server_size"),
                                           core=request.POST.get("server_core_num"),
                                           ip=None)
        this_server_manage_num += 1

        ServerLocation.objects.create(
            server_pk=new_server,
            rack_pk=None,
            rackLocation=None,
            realLocation=request.POST.get('server_location'))


def add_switches(request, new_asset):
    # add switches
    switch_number = int(request.POST.get("switch_number"))
    temp_switch = Switch.objects.filter(manageNum__startswith="N" + str(new_asset.acquisitionDate)[2:4]).order_by(
        '-manageNum').first()
    if temp_switch:
        this_switch_manage_num = int(temp_switch.manageNum[1:]) + 1
    else:
        this_switch_manage_num = int(str(new_asset.acquisitionDate)[2:4]) * 1000 + 1
    for i in range(0, switch_number):
        new_switch = Switch.objects.create(manageNum="N" + str(this_switch_manage_num),
                                           assetInfo=new_asset,
                                           manageSpec=new_asset.assetName,
                                           isInRack=False,
                                           size=request.POST.get("switch_size"),
                                           serviceOn=False,
                                           ip="127.0.0.1")
        this_switch_manage_num += 1

        SwitchLocation.objects.create(
            switch=new_switch,
            rack=None,
            rackLocation=None,
            realLocation=str(request.POST.get('switch_location')))


def add_racks(request, new_asset):
    # add racks
    rack_number = int(request.POST.get("rack_number"))
    temp_rack = Rack.objects.filter(manageNum__startswith="R" + str(new_asset.acquisitionDate)[2:4]).order_by(
        '-manageNum').first()
    if temp_rack:
        this_rack_manage_num = int(temp_rack.manageNum[1:]) + 1
    else:
        this_rack_manage_num = int(str(new_asset.acquisitionDate)[2:4]) * 1000 + 1

    for i in range(0, rack_number):
        new_rack = Rack.objects.create(manageNum="R" + str(this_rack_manage_num),
                                       assetInfo=new_asset,
                                       manageSpec=new_asset.assetName,
                                       size=request.POST.get("rack_size"),
                                       location=str(request.POST.get("rack_location")))
        this_rack_manage_num += 1


def add_storages(request, new_asset):
    # add storages
    storage_number = int(request.POST.get("storage_number"))
    temp_storage = StorageAsset.objects.filter(
        manageNum__startswith="D" + str(new_asset.acquisitionDate)[2:4]).order_by(
        '-manageNum').first()
    if temp_storage:
        this_storage_manage_num = int(temp_storage.manageNum[1:]) + 1
    else:
        this_storage_manage_num = int(str(new_asset.acquisitionDate)[2:4]) * 1000 + 1

    for i in range(0, storage_number):
        new_storage_asset = StorageAsset.objects.create(manageNum="D" + str(this_storage_manage_num),
                                                        assetInfo=new_asset,
                                                        manageSpec=request.POST.get("manage_spec"),
                                                        location=request.POST.get("storage_location"))
        new_storage = Storage.objects.create(storageAsset=new_storage_asset,
                                             enrollDate=new_asset.acquisitionDate,
                                             diskSpec=request.POST.get("disk_spec"),
                                             allocUnitSize=request.POST.get("alloc_size"),
                                             Vol=request.POST.get("disk_vol"),
                                             storageAssetName="속해있는 장치 명으로 수정하세요")

        this_storage_manage_num += 1


# 언제 어디서든 자산번호 클릭하면 나옵니다.
def asset_detail(request):
    searchText = request.GET.get("data")
    assetList = Asset.objects.filter(Q(assetNum=searchText) | Q(assetName=searchText) | Q(standard=searchText))
    if assetList.count() == 0:
        return HttpResponse("찾으시는 제품이 없습니다.")
    asset = assetList[0]
    asset_temp_list = Server.objects.select_related('location', 'assetInfo', 'location__rack_pk').filter(
        assetInfo=asset)
    temp_list = []
    for server in asset_temp_list:
        temp_dict = dict()
        # temp_dict['assetnum'] = server.assetInfo.assetNum
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
    asset_server_list = temp_list

    asset_temp_list = Switch.objects.select_related('location', 'assetInfo', 'location__rack').filter(assetInfo=asset)
    temp_list = []
    for switch in asset_temp_list:
        temp_dict = dict()
        # temp_dict['assetNum'] = switch.assetInfo.assetNum
        temp_dict['manageNum'] = switch.manageNum
        temp_dict['manageSpec'] = switch.manageSpec
        temp_dict['ip'] = switch.ip
        temp_location = switch.location
        if temp_location.rack is not None:
            temp_dict['location'] = temp_location.rack.location
        else:
            temp_dict['location'] = temp_location.realLocation
        temp_dict['onOff'] = True
        temp_list.append(temp_dict)
    asset_switch_list = temp_list

    asset_storage_list = StorageAsset.objects.filter(assetInfo=asset.id)

    asset_temp_list = Rack.objects.filter(assetInfo=asset.id)
    temp_list = []
    for rack in asset_temp_list:
        temp_dict = dict()
        # temp_dict['assetNum'] = rack.assetInfo.assetNum
        temp_dict['manageNum'] = rack.manageNum
        temp_dict['manageSpec'] = rack.manageSpec
        temp_dict['size'] = rack.size
        temp_dict['location'] = rack.location
        temp_list.append(temp_dict)
    asset_rack_list = temp_list
    context = {'asset_list': asset, 'asset_server_list': asset_server_list, 'asset_switch_list': asset_switch_list,
               'asset_storage_list': asset_storage_list, 'asset_rack_list': asset_rack_list}
    return render(request, 'dbApp/asset_detail.html', context)


#
def rack_detail(request):
    searchText = request.GET.get("data")
    rackname = None
    try:
        rack = Rack.objects.filter(Q(manageNum=searchText) | Q(manageSpec=searchText) | Q(location=searchText))[0]
        rackname = rack.manageNum
    except:
        return HttpResponse("찾으시는 제품이 없습니다.")

    rack_list = {}
    rack_name = {}
    rack_query_list = Rack.objects.filter(manageNum=rackname)
    rack_location = ""
    print(rack_query_list)
    for rack in rack_query_list:
        temp = rack.manageNum
        temp_name = rack.location
        temp_name = temp_name.split("-")
        rack_location = temp_name[0]
        temp_name = temp_name[1]
        #temp_name = rack.location[-3:]  # ex) C03
        rack_list[temp] = []
        rack_name[temp_name] = temp

    my_prefetch = Prefetch('ss_server', queryset=ServerService.objects.select_related('service'), to_attr="services")
    server_asset_list = Server.objects.select_related('location', 'location__rack_pk').prefetch_related(my_prefetch).filter(location__rack_pk=rack_query_list)
    switch_asset_list = Switch.objects.select_related('location', 'location__rack').filter(location__rack=rack_query_list)

    # make server list for rack
    for server in server_asset_list:
        temp_subDict = dict()
        temp_subDict['assetNum'] = server.assetInfo.assetNum
        temp_subDict['manageNum'] = server.manageNum
        temp_subDict['manageSpec'] = server.manageSpec
        temp_subDict['core'] = server.core
        temp_subDict['ip'] = server.ip
        temp_subDict['size'] = server.size
        if len(server.services) is not 0:
            temp_serverservice = server.services[0]
            temp_subDict['use'] = temp_serverservice.Use
            temp_service = temp_serverservice.service
            temp_subDict['serviceName'] = temp_service.serviceName
            temp_subDict['color'] = temp_service.color
        temp_location = server.location
        if temp_location.rack_pk is not None:
            temp_subDict['rack_pk'] = temp_location.rack_pk.manageNum
            temp_subDict['rackLocation'] = temp_location.rackLocation
            rack_list[temp_subDict['rack_pk']].append(temp_subDict)
    # make server list for rack
    for switch in switch_asset_list:
        temp_subDict = dict()
        temp_subDict['assetNum'] = server.assetInfo.assetNum
        temp_subDict['manageNum'] = switch.manageNum
        temp_subDict['manageSpec'] = switch.manageSpec
        temp_subDict['ip'] = switch.ip
        temp_subDict['use'] = switch.serviceOn
        temp_subDict['size'] = switch.size
        temp_subDict['color'] = '255, 204, 255'

        temp_location = switch.location
        if temp_location.rack is not None:
            temp_subDict['rack_pk'] = temp_location.rack.manageNum
            temp_subDict['rackLocation'] = temp_location.rackLocation
            rack_list[temp_subDict['rack_pk']].append(temp_subDict)
    rack_total = []
    for rack in rack_name:
        temp = dict()
        temp['id'] = rack_name[rack]
        temp['list'] = sorted(rack_list[temp['id']], key=lambda k: k['rackLocation'], reverse=True)
        temp['name'] = rack
        temp['location'] = rack_location
        rack_total.append(temp)
    data = []
    for rack in rack_total:
        position = [None] * 42
        for inrack in rack['list']:
            position[inrack["rackLocation"]] = inrack
        data.append({'data': list(reversed(position)), 'rack': rack})
    context = {'rack_list': rack_total, 'data': data}
    return render(request, 'dbApp/rack_detail.html', context)


def server_detail(request):
    searchText = request.GET.get("data")
    serverList = Server.objects.filter(Q(manageNum=searchText) | Q(manageSpec=searchText) | Q(ip=searchText))
    if serverList.count() == 0:
        return HttpResponse("찾으시는 제품이 없습니다.")
    server = serverList[0]
    return HttpResponse("서버 디테일 페이지 이고 서버 관리번호는" + server.manageNum + "입니다.")


def switch_detail(request):
    searchText = request.GET.get("data")
    switchList = Asset.objects.filter(Q(manageNum=searchText) | Q(manageSpec=searchText) | Q(ip=searchText))
    if switchList.count() == 0:
        return HttpResponse("찾으시는 제품이 없습니다.")
    switch = switchList[0]
    return HttpResponse("스위치 디테일 페이지 이고 스위치 이름은" + switch.manageNum + "입니다.")


# def asset_detail(request):
#    searchText = request.GET.get("data")
#    assetList = Asset.objects.filter(Q(assetNum=searchText) | Q(assetName=searchText) | Q(standard=searchText))
#    if assetList.count() == 0:
#        return HttpResponse("찾으시는 제품이 없습니다.")
#    asset = assetList[0]
#    return HttpResponse("에셋 디테일 페이지 이고 자산번호는" + asset.assetNum + "입니다.")


def search_assets(request):
    searchText = request.GET.get("searchText")
    print(searchText)
    return render(request, 'dbApp/searchResult.html', {})


def edit_asset(request):
    selected = request.GET.get("data")
    return HttpResponse("자산번호" + selected + "를 수정하고싶니?")


def delete_asset(request, pk):
    try:
        assets = Asset.objects.filter(assetNum=pk).all()
        if assets.count() == 0:
            raise Asset.DoesNotExist
    except Asset.DoesNotExist:
        return HttpResponse("error", 404)
    assets.delete()
    return HttpResponse("ok")


def delete_one_asset(request, asset_type, manage_num):
    print("delete one asset")
    if asset_type == "server":
        try:
            server = Server.objects.filter(manageNum=manage_num)
            if server.count() == 0:
                raise Server.DoesNotExist
        except Server.DoesNotExist:
            return HttpResponse("error", 404)
        server.delete()
    elif asset_type == "switch":
        try:
            switch = Switch.objects.filter(manageNum=manage_num)
            if switch.count() == 0:
                raise Switch.DoesNotExist
        except Switch.DoesNotExist:
            return HttpResponse("error", 404)
        switch.delete()
    elif asset_type == "rack":
        try:
            rack = Rack.objects.filter(manageNum=manage_num)
            if Rack.count() == 0:
                raise Rack.DoesNotExist
        except Rack.DoesNotExist:
            return HttpResponse("error", 404)
        rack.delete()

    server_prefetch = Prefetch('server', to_attr='servers')
    switch_prefetch = Prefetch('switch', to_attr='switches')
    storage_prefetch = Prefetch('storageasset', to_attr='storages')
    rack_prefetch = Prefetch('rack', to_attr='racks')

    asset_total_list = Asset.objects.all().prefetch_related(server_prefetch, switch_prefetch, storage_prefetch,
                                                            rack_prefetch)
    for asset in asset_total_list:
        server_num = len(asset.servers)
        switch_num = len(asset.switches)
        storage_num = len(asset.storages)
        rack_num = len(asset.racks)
        total_num = server_num + switch_num + storage_num + rack_num
        if total_num == 0:
            target_asset = Asset.objects.filter(assetNum=asset.assetNum)
            target_asset.delete()
    return HttpResponse("ok")
