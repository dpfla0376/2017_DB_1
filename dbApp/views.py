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

is_test = False


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
    if is_test:
        return User.objects.get(username='sangwon0001@gmail.com')
    try:
        username = session['usertoken']
        return User.objects.get(username=username)
    except KeyError:
        return None


def make_asset_dict_list(asset_list):
    temp_list = []
    for asset in asset_list:
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
    return temp_list


def make_server_dict_list(server_list):
    temp_list = list()
    for server in server_list:
        temp_dict = dict()
        temp_dict['assetnum'] = server.assetInfo.assetNum
        temp_dict['managenum'] = server.manageNum
        temp_dict['managespec'] = server.manageSpec
        temp_dict['core'] = server.core
        temp_dict['ip'] = server.ip
        temp_dict['size'] = server.size

        if len(server.services) is not 0:
            temp_serverservice = server.services[0]
            temp = temp_serverservice.Use
            if (temp == True):
                temp_dict['onoff'] = "On"
            else:
                temp_dict['onoff'] = "Off"

        temp_location = server.location
        if temp_location.rack_pk is not None:
            temp_dict['location'] = temp_location.rack_pk.location
        else:
            temp_dict['location'] = temp_location.realLocation
        temp_list.append(temp_dict)
    return temp_list


def make_switch_dict_list(switch_list):
    temp_list = []
    for switch in switch_list:
        temp_dict = {}
        temp_dict['assetNum'] = switch.assetInfo.assetNum
        temp_dict['manageNum'] = switch.manageNum
        temp_dict['manageSpec'] = switch.manageSpec
        temp_dict['size'] = switch.size
        temp_dict['ip'] = switch.ip
        temp_location = switch.location
        if temp_location.rack is not None:
            temp_dict['location'] = temp_location.rack.location
        else:
            temp_dict['location'] = temp_location.realLocation
        temp = switch.serviceOn
        if (temp == True):
            temp_dict['onOff'] = 'On'
        else:
            temp_dict['onOff'] = 'Off'
        temp_list.append(temp_dict)
    return temp_list


def make_rack_dict_list(rack_list):
    temp_list = []
    for rack in rack_list:
        temp_dict = {}
        temp_dict['assetNum'] = rack.assetInfo.assetNum
        temp_dict['manageNum'] = rack.manageNum
        temp_dict['manageSpec'] = rack.manageSpec
        temp_dict['size'] = rack.size
        temp_dict['location'] = rack.location
        temp_list.append(temp_dict)
    return temp_list


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

    cursor.execute('SELECT sv.id, ss.uses, sa.storageForm AS type, SUM(ss.allocSize) as sizes ' +
                   'FROM `dbApp_service` sv ' +
                   'INNER JOIN `dbApp_storageservice` ss ON ss.service_id = sv.id ' +
                   'INNER JOIN `dbApp_storage` st ON st.id = ss.storage_id ' +
                   'INNER JOIN `dbApp_storageasset` sa ON sa.id = st.storageAsset_id ' +
                   'GROUP BY sv.id, sa.storageForm, ss.uses')
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
        user.save()
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


def sign_out(request):
    request.session.clear()
    return HttpResponseRedirect('/dbApp/')


def welcome(request):
    return render(request, 'dbApp/welcome_page.html', {})


def asset_total(request):
    #############################로그인#############################
    user = getUser(request.session)  # 여기부터 아래까지 총 3줄이 로그인 검증 부분입니당
    if user is None:
        return HttpResponseRedirect('/dbApp/')
    context = {'username': user.first_name}

    #############################로그인#############################
    server_prefetch = Prefetch('server', to_attr='servers')
    switch_prefetch = Prefetch('switch', to_attr='switches')
    storage_prefetch = Prefetch('storageasset', to_attr='storages')
    rack_prefetch = Prefetch('rack', to_attr='racks')
    asset_total_list = Asset.objects.all().prefetch_related(server_prefetch, switch_prefetch, storage_prefetch,
                                                            rack_prefetch)

    context['asset_total_list'] = make_asset_dict_list(asset_total_list)
    return render(request, 'dbApp/asset_total.html', context)


def switch_asset(request):
    #############################로그인#############################
    user = getUser(request.session)  # 여기부터 아래까지 총 3줄이 로그인 검증 부분입니당
    if user is None:
        return HttpResponseRedirect('/dbApp/')
    context = {'username': user.first_name}

    #############################로그인#############################
    switch_asset_list = Switch.objects.select_related('assetInfo', 'location', 'location__rack').all()
    context['switch_asset_list'] = make_switch_dict_list(switch_asset_list)
    return render(request, 'dbApp/switch_asset.html', context)


def server_asset(request):
    #############################로그인#############################
    user = getUser(request.session)  # 여기부터 아래까지 총 3줄이 로그인 검증 부분입니당
    if user is None:
        return HttpResponseRedirect('/dbApp/')
    context = {'username': user.first_name}

    #############################로그인#############################
    start_time = time.time()
    my_prefetch = Prefetch('ss_server', queryset=ServerService.objects.select_related('service'), to_attr="services")
    server_asset_list = Server.objects.select_related('location', 'assetInfo', 'location__rack_pk').prefetch_related(
        my_prefetch).all()
    context['server_asset_list'] = make_server_dict_list(server_asset_list)
    temppp = render(request, 'dbApp/server_asset.html', context)
    print("--- %s seconds ---" % (time.time() - start_time))
    return temppp
    # return HttpResponse(temp_list)


# rack_asset 에 대한 페이지. Rack list 클릭하면 나옵니다.
def rack_asset(request):
    #############################로그인#############################
    user = getUser(request.session)  # 여기부터 아래까지 총 3줄이 로그인 검증 부분입니당
    if user is None:
        return HttpResponseRedirect('/dbApp/')
    context = {'username': user.first_name}

    #############################로그인#############################
    rack_asset_list = Rack.objects.select_related('assetInfo').all()
    context['rack_asset_list'] = make_rack_dict_list(rack_asset_list)
    return render(request, 'dbApp/rack_asset.html', context)


def service_resources(request):  # 서비스의 리소스를 보여준다.
    #############################로그인#############################
    user = getUser(request.session)  # 여기부터 아래까지 총 3줄이 로그인 검증 부분입니당
    if user is None:
        return HttpResponseRedirect('/dbApp/')
    context = {'username': user.first_name}

    #############################로그인#############################
    service_list = Service.objects.all()
    temp_list = []
    for service in service_list:
        temp_dict = {}
        temp_dict['id'] = service.id
        temp_dict['name'] = service.serviceName
        temp_list.append(temp_dict)
    context['service_list'] = temp_list
    return render(request, 'dbApp/service_resources.html', context)


def storage_detail(request):
    #############################로그인#############################
    user = getUser(request.session)  # 여기부터 아래까지 총 3줄이 로그인 검증 부분입니당
    if user is None:
        return HttpResponseRedirect('/dbApp/')
    context = {'username': user.first_name}

    #############################로그인#############################
    searchText = request.GET.get("data")

    cursor = connection.cursor()
    cursor.execute(
        'SELECT * FROM `dbApp_asset` ' +
        'INNER JOIN `dbApp_storageasset` ON dbApp_storageasset.assetInfo_id = dbApp_asset.id ' +
        'WHERE dbApp_storageasset.manageNum = ' + '\"' + searchText + '\"')
    storage_list = dictFetchall(cursor)

    return render(request, 'dbApp/storage_detail.html', {'storage_list': storage_list[0], 'username': user.first_name})


def storage_asset(request):
    #############################로그인#############################
    user = getUser(request.session)  # 여기부터 아래까지 총 3줄이 로그인 검증 부분입니당
    if user is None:
        return HttpResponseRedirect('/dbApp/')
    context = {'username': user.first_name}
    #############################로그인#############################
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM `dbApp_asset` ' +
                   'INNER JOIN `dbApp_storageasset` ON dbApp_storageasset.assetInfo_id = dbApp_asset.id ')
    storage_list = dictFetchall(cursor)
    return render(request, 'dbApp/storage_asset.html', {'storage_list': storage_list, 'username': user.first_name})


def storage_total(request):
    #############################로그인#############################
    user = getUser(request.session)  # 여기부터 아래까지 총 3줄이 로그인 검증 부분입니당
    if user is None:
        return HttpResponseRedirect('/dbApp/')
    context = {'username': user.first_name}

    #############################로그인#############################
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM `dbApp_asset` ' +
                   'INNER JOIN `dbApp_storageasset` ON dbApp_storageasset.assetInfo_id = dbApp_asset.id ' +
                   'INNER JOIN `dbApp_storage` ON dbApp_storageasset.id = dbApp_storage.storageAsset_id ' +
                   'INNER JOIN `dbApp_storageservice` ON dbApp_storageservice.storage_id = dbApp_storage.id ' +
                   'INNER JOIN `dbApp_service` ON dbApp_storageservice.service_id = dbApp_service.id ')
    db_storage_list = dictFetchall(cursor)

    storage_list = {}
    for row in db_storage_list:
        spec = row['storageAssetName']

        if not spec in storage_list:
            storage_list[spec] = {
                'name': spec,
                'totalCount': 0,
                'enrollList': {}
            }

        enroll = row['enrollDate'].isoformat()
        if not enroll in storage_list[spec]['enrollList']:
            storage_list[spec]['enrollList'][enroll] = {
                'date': enroll,
                'enrollCount': 0,
                'diskList': {}
            }

        disk = row['diskSpec']
        if not disk in storage_list[spec]['enrollList'][enroll]['diskList']:
            storage_list[spec]['enrollList'][enroll]['diskList'][disk] = {
                'manageNum': row['manageNum'],
                'diskSpec': disk,
                'list': [],
                'vol': row['Vol'],
                'usageTotal': 0,
                'remainSize': row['Vol'],
                'diskSpec': row['diskSpec'],
                'allocUnitSize': row['allocUnitSize'],
                'storageForm': row['storageForm'],
                'diskCount': 0
            }

        storage_list[spec]['totalCount'] = storage_list[spec]['totalCount'] + 1
        storage_list[spec]['enrollList'][enroll]['enrollCount'] += 1
        storage_list[spec]['enrollList'][enroll]['diskList'][disk]['diskCount'] += 1
        storage_list[spec]['enrollList'][enroll]['diskList'][disk]['usageTotal'] += row['allocSize']
        storage_list[spec]['enrollList'][enroll]['diskList'][disk]['remainSize'] -= row['allocSize']
        storage_list[spec]['enrollList'][enroll]['diskList'][disk]['usageTotal'] = \
            round(storage_list[spec]['enrollList'][enroll]['diskList'][disk]['usageTotal'], 2)
        storage_list[spec]['enrollList'][enroll]['diskList'][disk]['list'].append({
            'allocSize': row['allocSize'],
            'serviceName': row['serviceName'],
            'usage': row['usage']
        })
    print(storage_list)
    return render(request, 'dbApp/storage_total.html', {'storage_list': storage_list, 'username': user.first_name});


def check_in_list(mylist, mystring):
    for temp_dict in mylist:
        if temp_dict['storagename'] == mystring:
            return temp_dict
    return None


def check_in_list_date(mylist, mystring):
    for temp_dict in mylist:
        if temp_dict['date'] == mystring:
            return temp_dict
    return None


def service_storage2(request):
    #############################로그인#############################
    user = getUser(request.session)  # 여기부터 아래까지 총 3줄이 로그인 검증 부분입니당
    if user is None:
        return HttpResponseRedirect('/dbApp/')
    context = {'username': user.first_name}

    #############################로그인#############################
    my_prefetch = Prefetch('storage_service', queryset=StorageService.objects.select_related('service'),
                           to_attr="services")
    storage_list = Storage.objects.select_related('storageAsset', 'storageAsset__assetInfo').all().prefetch_related(
        my_prefetch)
    temp_list = list()
    for storagee in storage_list:
        temp_dict = {}
        temp_dict['storageassetname'] = storagee.storageAssetName
        temp_dict['vol'] = storagee.Vol
        temp_dict['allocunitsize'] = storagee.allocUnitSize
        temp_dict['diskspec'] = storagee.diskSpec
        temp_dict['storageform'] = storagee.storageAsset.storageForm
        temp_float = 0
        temp_list2 = list()
        temp_dict['servicecount'] = len(storagee.services)
        for storageservice in storagee.services:
            temp_dict2 = {}
            temp_float += storageservice.allocSize
            temp_dict2['allocsize'] = storageservice.allocSize
            temp_dict2['servicename'] = storageservice.service.serviceName
            temp_dict2['usage'] = storageservice.usage
            temp_list2.append(temp_dict2)
        temp_dict['remain'] = storagee.Vol - temp_float
        temp_dict['servicelist'] = temp_list2
        temp_date = check_in_list_date(temp_list, storagee.enrollDate.isoformat())
        if temp_date is not None:
            temp_date['storagecount'] += 1
            temp_date['storagelist'].append(temp_dict)
        else:
            date_dict = {}
            date_dict['date'] = storagee.enrollDate.isoformat()
            date_dict['storagelist'] = [temp_dict]
            date_dict['storagecount'] = 1
            date_dict['storageassetname'] = storagee.storageAssetName
        temp_list.append(date_dict)
    final_list2 = list()
    for dateDict in temp_list:
        tempp = check_in_list(final_list2, dateDict['storageassetname'])
        if tempp is not None:
            tempp['dateList'].append(dateDict)
            tempp['datecount'] += 1
        else:
            temp_dict = {}
            temp_dict['storagename'] = dateDict['storageassetname']
            temp_dict['dateList'] = [dateDict]
            temp_dict['datecount'] = 1
            final_list2.append(temp_dict)
    return HttpResponse(json.dumps(final_list2))


def service_storage(request):
    #############################로그인#############################
    user = getUser(request.session)  # 여기부터 아래까지 총 3줄이 로그인 검증 부분입니당
    if user is None:
        return HttpResponseRedirect('/dbApp/')
    #############################로그인#############################
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM `dbApp_asset` ' +
                   'INNER JOIN `dbApp_storageasset` ON dbApp_storageasset.assetInfo_id = dbApp_asset.id ' +
                   'INNER JOIN `dbApp_storage` ON dbApp_storageasset.id = dbApp_storage.storageAsset_id ' +
                   'INNER JOIN `dbApp_storageservice` ON dbApp_storageservice.storage_id = dbApp_storage.id ' +
                   'INNER JOIN `dbApp_service` ON dbApp_storageservice.service_id = dbApp_service.id ')
    db_storage_list = dictFetchall(cursor)

    storage_list = {}
    for row in db_storage_list:
        spec = row['storageAssetName']
        #        if not hasattr(storage_list, spec):
        if not spec in storage_list:
            storage_list[spec] = {
                'name': spec,
                'totalCount': 0,
                'enrollList': {}
            }
        enroll = row['enrollDate'].isoformat()
        if not enroll in storage_list[spec]['enrollList']:
            storage_list[spec]['enrollList'][enroll] = {
                'date': enroll,
                'enrollCount': 0,
                'diskList': {}

            }

        disk = row['diskSpec']
        if not disk in storage_list[spec]['enrollList'][enroll]['diskList']:
            storage_list[spec]['enrollList'][enroll]['diskList'][disk] = {
                'diskSpec': disk,
                'list': [],
                'vol': row['Vol'],
                'usageTotal': 0,
                'remainSize': row['Vol'],
                'diskSpec': row['diskSpec'],
                'allocUnitSize': row['allocUnitSize'],
                'storageForm': row['storageForm'],
                'diskCount': 0
            }

        storage_list[spec]['totalCount'] = storage_list[spec]['totalCount'] + 1
        storage_list[spec]['enrollList'][enroll]['enrollCount'] += 1
        storage_list[spec]['enrollList'][enroll]['diskList'][disk]['diskCount'] += 1
        storage_list[spec]['enrollList'][enroll]['diskList'][disk]['usageTotal'] += row['allocSize']
        storage_list[spec]['enrollList'][enroll]['diskList'][disk]['remainSize'] -= row['allocSize']
        storage_list[spec]['enrollList'][enroll]['diskList'][disk]['usageTotal'] = \
            round(storage_list[spec]['enrollList'][enroll]['diskList'][disk]['usageTotal'], 2)
        storage_list[spec]['enrollList'][enroll]['diskList'][disk]['list'].append({
            'allocSize': row['allocSize'],
            'serviceName': row['serviceName'],
            'usage': row['usage']
        })
    return render(request, 'dbApp/storage_service.html', {'storage_list': storage_list, 'username': user.first_name});


def service_detail(request, pk):
    #############################로그인#############################
    user = getUser(request.session)  # 여기부터 아래까지 총 3줄이 로그인 검증 부분입니당
    if user is None:
        return HttpResponseRedirect('/dbApp/')
    #############################로그인#############################
    cursor = connection.cursor()
    cursor.execute(
        'SELECT assetNum, s.manageNum,acquisitionDate, s.manageSpec, location, core, ip, assetName, standard, maintenanceYear, realLocation, isInRack, ss.Use ' +
        'FROM `dbApp_asset` a INNER JOIN `dbApp_server` s ON a.id = s.assetInfo_id ' +
        'INNER JOIN `dbApp_serverlocation` sl ON sl.server_pk_id = s.id ' +
        'INNER JOIN `dbApp_rack` r ON r.id = sl.rack_pk_id ' +
        'INNER JOIN dbApp_serverservice ss ON ss.server_id = s.id ' +
        'WHERE ss.service_id = ' + pk)
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
                                                         'TAPE': disk_TAPE,
                                                         'username': user.first_name
                                                         });


def service_add_server(request, pk):
    #############################로그인#############################
    user = getUser(request.session)  # 여기부터 아래까지 총 3줄이 로그인 검증 부분입니당
    if user is None:
        return HttpResponseRedirect('/dbApp/')
    context = {'username': user.first_name}

    #############################로그인#############################

    my_prefetch = Prefetch('ss_server', to_attr="services")
    server_list = Server.objects.select_related('assetInfo', 'location', 'location__rack_pk').all().prefetch_related(
        my_prefetch)
    server_list2 = list()
    for server in server_list:
        if len(server.services) == 0:
            server_list2.append(server)

    context['server_asset_list'] = make_server_dict_list(server_list2)
    context['service'] = pk

    return render(request, 'dbApp/service_add_server.html', context)


def service_add_server_api(request, pk, manage_num):
    #############################로그인#############################
    user = getUser(request.session)  # 여기부터 아래까지 총 3줄이 로그인 검증 부분입니당
    if user is None:
        return HttpResponseRedirect('/dbApp/')
    #############################로그인#############################

    server = Server.objects.get(manageNum=manage_num)
    service = Service.objects.get(id=pk)
    try:
        ServerService.objects.get(server=server, service=service)
    except:
        ServerService.objects.create(server=server, service=service)
    return HttpResponseRedirect('/dbApp/resource/service/' + str(pk) + '/addserver/')


def service_add_san(request, pk):
    #############################로그인#############################
    user = getUser(request.session)  # 여기부터 아래까지 총 3줄이 로그인 검증 부분입니당
    if user is None:
        return HttpResponseRedirect('/dbApp/')
    context = {'username': user.first_name}
    #############################로그인#############################

    my_prefetch = Prefetch('storage_service', to_attr="services")
    storage_list = Storage.objects.select_related('storageAsset').filter(
        storageAsset__storageForm='SAN').prefetch_related(my_prefetch)
    storage_list2 = list()
    for storage in storage_list:
        remain_size = storage.Vol
        for storageservice in storage.services:
            remain_size -= storageservice.allocSize
        if remain_size > 0:
            storage_list2.append(storage)
    storage_list = list()
    for storage in storage_list2:
        temp_san_dict = {}
        temp_san_dict['managenum'] = storage.id
        temp_san_dict['name'] = storage.storageAssetName
        temp_san_dict['enrolldate'] = storage.enrollDate
        temp_san_dict['spec'] = storage.diskSpec
        temp_san_dict['format'] = storage.storageAsset.storageForm
        temp_san_dict['alloc_size'] = storage.allocUnitSize
        temp_san_dict['vol'] = storage.Vol
        remain_size = storage.Vol
        for storageservice in storage.services:
            remain_size -= storageservice.allocSize
        if remain_size > 0:
            temp_san_dict['remain_size'] = remain_size
        storage_list.append(temp_san_dict)
    context['storage_asset_list'] = storage_list
    context['service'] = pk
    return render(request, 'dbApp/service_add_san.html', context)


def service_add_san_api(request, pk, managenum):
    #############################로그인#############################
    user = getUser(request.session)  # 여기부터 아래까지 총 3줄이 로그인 검증 부분입니당
    if user is None:
        return HttpResponseRedirect('/dbApp/')
    #############################로그인#############################
    storage = Storage.objects.get(id=managenum)
    remain_size = storage.Vol
    for storageservice in StorageService.objects.filter(storage=storage):
        remain_size -= storageservice.allocSize
    service = Service.objects.get(id=pk)
    if remain_size * 1000 > storage.allocUnitSize * int(request.POST['count']):
        try:
            StorageService.objects.get(storage=storage, service=service, usage=request.POST['usage'])
        except:
            StorageService.objects.create(storage=storage, service=service, usage=request.POST['usage'],
                                          allocSize=storage.allocUnitSize * int(request.POST['count']) / 1000)
    return HttpResponseRedirect('/dbApp/resource/service/' + str(pk) + '/addsan/')


def service_add_nas(request, pk):
    #############################로그인#############################
    user = getUser(request.session)  # 여기부터 아래까지 총 3줄이 로그인 검증 부분입니당
    if user is None:
        return HttpResponseRedirect('/dbApp/')
    context = {'username': user.first_name}
    #############################로그인#############################

    my_prefetch = Prefetch('storage_service', to_attr="services")
    storage_list = Storage.objects.select_related('storageAsset').filter(
        storageAsset__storageForm='NAS').prefetch_related(my_prefetch)
    storage_list2 = list()
    for storage in storage_list:
        remain_size = storage.Vol
        for storageservice in storage.services:
            remain_size -= storageservice.allocSize
        if remain_size > 0:
            storage_list2.append(storage)
    storage_list = list()
    for storage in storage_list2:
        temp_san_dict = {}
        temp_san_dict['managenum'] = storage.id
        temp_san_dict['name'] = storage.storageAssetName
        temp_san_dict['enrolldate'] = storage.enrollDate
        temp_san_dict['spec'] = storage.diskSpec
        temp_san_dict['format'] = storage.storageAsset.storageForm
        temp_san_dict['alloc_size'] = storage.allocUnitSize
        temp_san_dict['vol'] = storage.Vol
        remain_size = storage.Vol
        for storageservice in storage.services:
            remain_size -= storageservice.allocSize
        if remain_size > 0:
            temp_san_dict['remain_size'] = remain_size
        storage_list.append(temp_san_dict)
    context['storage_asset_list'] = storage_list
    context['service'] = pk
    return render(request, 'dbApp/service_add_nas.html', context)


def service_add_nas_api(request, pk, managenum):
    #############################로그인#############################
    user = getUser(request.session)  # 여기부터 아래까지 총 3줄이 로그인 검증 부분입니당
    if user is None:
        return HttpResponseRedirect('/dbApp/')
    context = {'username': user.first_name}
    #############################로그인#############################
    storage = Storage.objects.get(id=managenum)
    remain_size = storage.Vol
    for storageservice in StorageService.objects.filter(storage=storage):
        remain_size -= storageservice.allocSize
    service = Service.objects.get(id=pk)
    if remain_size * 1000 > int(request.POST['count']):
        try:
            StorageService.objects.get(storage=storage, service=service, usage=request.POST['usage'])
        except:
            StorageService.objects.create(storage=storage, service=service, usage=request.POST['usage'],
                                          allocSize=int(request.POST['count']) / 1000)
    return HttpResponseRedirect('/dbApp/resource/service/' + str(pk) + '/addnas/')


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
    #############################로그인#############################
    user = getUser(request.session)  # 여기부터 아래까지 총 3줄이 로그인 검증 부분입니당
    if user is None:
        return HttpResponseRedirect('/dbApp/')
    context = {'username': user.first_name}

    #############################로그인#############################
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
        temp_subDict['color'] = '255,255,255'
        if len(server.services) is not 0:
            temp_serverservice = server.services[0]
            temp = temp_serverservice.Use
            if (temp == True):
                temp_subDict['use'] = "On"
            else:
                temp_subDict['use'] = "Off"
            temp_service = temp_serverservice.service
            temp_subDict['serviceName'] = temp_service.serviceName
            temp_subDict['color'] = temp_service.color
        temp_location = server.location
        if temp_location.rack_pk is not None:
            temp_subDict['rack_pk'] = temp_location.rack_pk.manageNum
            temp_subDict['rackLocation'] = temp_location.rackLocation
            rack_list[temp_subDict['rack_pk']].append(temp_subDict)
            temp_subDict['drawIndex'] = int(temp_subDict['rackLocation']) + int(temp_subDict['size']) - 1

    # make server list for rack
    for switch in switch_asset_list:
        temp_subDict = dict()
        temp_subDict['manageNum'] = switch.manageNum
        temp_subDict['manageSpec'] = switch.manageSpec
        temp_subDict['ip'] = switch.ip
        temp_subDict['use'] = switch.serviceOn
        temp_subDict['size'] = switch.size
        if (temp_subDict['use'] == True):
            temp_subDict['color'] = '255, 204, 255'
        else:
            temp_subDict['color'] = '255, 255, 204'
        temp_subDict['serviceName'] = ''
        temp_location = switch.location
        if temp_location.rack is not None:
            temp_subDict['rack_pk'] = temp_location.rack.manageNum
            temp_subDict['rackLocation'] = temp_location.rackLocation
            rack_list[temp_subDict['rack_pk']].append(temp_subDict)
            temp_subDict['drawIndex'] = int(temp_subDict['rackLocation']) + int(temp_subDict['size']) - 1

    rack_total = []
    for rack in rack_name:
        temp = dict()
        temp['id'] = rack_name[rack]
        temp['list'] = sorted(rack_list[temp['id']], key=lambda k: k['rackLocation'], reverse=True)
        temp['name'] = rack
        rack_total.append(temp)
    data = []
    for rack in rack_total:
        # TODO 이 아랫부분 지워야됩니다.
        position = [None] * 42
        for inrack in rack['list']:
            position[(inrack['drawIndex']) - 1] = inrack
        data.append({'data': list(reversed(position)), 'rack': rack})
    context['rack_list'] = rack_total
    context['data'] = data
    print("--- %s seconds ---" % (time.time() - start_time))
    return render(request, 'dbApp/rack_info.html', context)


def insert_asset(request):
    #############################로그인#############################
    user = getUser(request.session)  # 여기부터 아래까지 총 3줄이 로그인 검증 부분입니당
    if user is None:
        return HttpResponseRedirect('/dbApp/')
    context = {'username': user.first_name}

    #############################로그인#############################
    asset_total_list = Asset.objects.all()
    context['asset_total_list'] = asset_total_list
    return render(request, 'dbApp/asset_total.html', context)


def add(request, add_type):
    #############################로그인#############################
    user = getUser(request.session)  # 여기부터 아래까지 총 3줄이 로그인 검증 부분입니당
    if user is None:
        return HttpResponseRedirect('/dbApp/')
    context = {'username': user.first_name}

    #############################로그인#############################
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

            context['messages'] = '완료되었습니다.'
            return render(request, 'dbApp/add_asset.html', context)

        elif add_type == "service":

            hex_color = request.POST.get("service_color").lstrip('#')
            rgb_tuple = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
            rgb = str(rgb_tuple[0]) + "," + str(rgb_tuple[1]) + "," + str(rgb_tuple[2])
            context = {}
            try:
                Service.objects.get(serviceName=request.POST.get("service_name"))
                context['messages'] = '이미 있는 서비스 입니다.'
            except Service.DoesNotExist:
                Service.objects.create(serviceName=request.POST.get("service_name"),
                                       makeDate=request.POST.get("service_make_date"),
                                       color=rgb)
                context['messages'] = '완료되었습니다.'

            return render(request, 'dbApp/add_service.html', context)
    else:
        if add_type == "asset":
            return render(request, 'dbApp/add_asset.html', context)
        elif add_type == "service":
            return render(request, 'dbApp/add_service.html', context)


def add_servers(request, new_asset):
    # add servers
    #############################로그인#############################
    user = getUser(request.session)  # 여기부터 아래까지 총 3줄이 로그인 검증 부분입니당
    if user is None:
        return HttpResponseRedirect('/dbApp/')
    context = {'username': user.first_name}

    #############################로그인#############################
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
                                           manageSpec=request.POST.get("server_manage_spec"),
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
    #############################로그인#############################
    user = getUser(request.session)  # 여기부터 아래까지 총 3줄이 로그인 검증 부분입니당
    if user is None:
        return HttpResponseRedirect('/dbApp/')
    context = {'username': user.first_name}

    #############################로그인#############################
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
                                           manageSpec=request.POST.get("switch_manage_spec"),
                                           isInRack=False,
                                           size=request.POST.get("switch_size"),
                                           serviceOn=False,
                                           ip=None)
        this_switch_manage_num += 1

        SwitchLocation.objects.create(
            switch=new_switch,
            rack=None,
            rackLocation=None,
            realLocation=str(request.POST.get('switch_location')))


def add_racks(request, new_asset):
    # add racks
    #############################로그인#############################
    user = getUser(request.session)  # 여기부터 아래까지 총 3줄이 로그인 검증 부분입니당
    if user is None:
        return HttpResponseRedirect('/dbApp/')
    context = {'username': user.first_name}

    #############################로그인#############################
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
                                       manageSpec=request.POST.get("rack_manage_spec"),
                                       size=request.POST.get("rack_size"),
                                       location=str(request.POST.get("rack_location")))
        this_rack_manage_num += 1


def add_storages(request, new_asset):
    # add storages
    #############################로그인#############################
    user = getUser(request.session)  # 여기부터 아래까지 총 3줄이 로그인 검증 부분입니당
    if user is None:
        return HttpResponseRedirect('/dbApp/')
    context = {'username': user.first_name}

    #############################로그인#############################
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


def service_detail2(request):
    #############################로그인#############################
    user = getUser(request.session)  # 여기부터 아래까지 총 3줄이 로그인 검증 부분입니당
    if user is None:
        return HttpResponseRedirect('/dbApp/')
    #############################로그인#############################
    searchText = request.GET.get("data")
    service_list = Service.objects.filter(Q(serviceName=searchText))
    if service_list.count() == 0:
        return HttpResponse("찾으시는 제품이 없습니다.")
    service = service_list[0]
    return HttpResponseRedirect('/dbApp/resource/service/' + str(service.id) + '/')


# 언제 어디서든 자산번호 클릭하면 나옵니다.
def asset_detail(request):
    #############################로그인#############################
    user = getUser(request.session)  # 여기부터 아래까지 총 3줄이 로그인 검증 부분입니당
    if user is None:
        return HttpResponseRedirect('/dbApp/')
    context = {'username': user.first_name}

    #############################로그인#############################
    searchText = request.GET.get("data")
    assetList = Asset.objects.filter(Q(assetNum=searchText) | Q(assetName=searchText) | Q(standard=searchText))
    if assetList.count() == 0:
        return HttpResponse("찾으시는 제품이 없습니다.")
    asset = assetList[0]

    my_prefetch = Prefetch('ss_server', queryset=ServerService.objects.select_related('service'), to_attr="services")
    asset_temp_list = Server.objects.select_related('location', 'assetInfo', 'location__rack_pk').prefetch_related(
        my_prefetch).filter(assetInfo=asset)
    # asset_temp_list = Server.objects.select_related('location', 'assetInfo', 'location__rack_pk').filter(assetInfo=asset)
    temp_list = []
    for server in asset_temp_list:
        temp_dict = dict()
        # temp_dict['assetnum'] = server.assetInfo.assetNum
        temp_dict['managenum'] = server.manageNum
        temp_dict['managespec'] = server.manageSpec
        temp_dict['core'] = server.core
        temp_dict['ip'] = server.ip
        temp_location = server.location
        if len(server.services) is not 0:
            temp_serverservice = server.services[0]
            temp_dict['use'] = temp_serverservice.Use
            temp_service = temp_serverservice.service
            temp_dict['serviceName'] = temp_service.serviceName
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
        temp = switch.serviceOn
        if (temp == True):
            temp_dict['onOff'] = 'On'
        else:
            temp_dict['onOff'] = 'Off'
        temp_list.append(temp_dict)
    asset_switch_list = temp_list

    cursor = connection.cursor()
    cursor.execute(
        'SELECT * FROM `dbApp_asset` ' +
        'INNER JOIN `dbApp_storageasset` ON dbApp_storageasset.assetInfo_id = dbApp_asset.id ' +
        'WHERE dbApp_storageasset.assetInfo_id = ' + '\"' + str(asset.id) + '\"')
    asset_storage_list = dictFetchall(cursor)

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
               'asset_storage_list': asset_storage_list, 'asset_rack_list': asset_rack_list,
               'username': user.first_name}
    return render(request, 'dbApp/asset_detail.html', context)


#
def rack_detail(request):
    #############################로그인#############################
    user = getUser(request.session)  # 여기부터 아래까지 총 3줄이 로그인 검증 부분입니당
    if user is None:
        return HttpResponseRedirect('/dbApp/')
    context = {'username': user.first_name}

    #############################로그인#############################
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
        # temp_name = rack.location[-3:]  # ex) C03
        rack_list[temp] = []
        rack_name[temp_name] = temp

    my_prefetch = Prefetch('ss_server', queryset=ServerService.objects.select_related('service'), to_attr="services")
    server_asset_list = Server.objects.select_related('location', 'location__rack_pk').prefetch_related(
        my_prefetch).filter(location__rack_pk=rack_query_list)
    switch_asset_list = Switch.objects.select_related('location', 'location__rack').filter(
        location__rack=rack_query_list)

    # make server list for rack
    for server in server_asset_list:
        temp_subDict = dict()
        temp_subDict['assetNum'] = server.assetInfo.assetNum
        temp_subDict['manageNum'] = server.manageNum
        temp_subDict['manageSpec'] = server.manageSpec
        temp_subDict['core'] = server.core
        temp_subDict['ip'] = server.ip
        temp_subDict['size'] = server.size
        temp_subDict['color'] = '255,255,255'
        if len(server.services) is not 0:
            temp_serverservice = server.services[0]
            temp = temp_serverservice.Use
            if (temp == True):
                temp_subDict['use'] = "On"
            else:
                temp_subDict['use'] = "Off"
            temp_service = temp_serverservice.service
            temp_subDict['serviceName'] = temp_service.serviceName
            temp_subDict['color'] = temp_service.color
        temp_location = server.location
        if temp_location.rack_pk is not None:
            temp_subDict['rack_pk'] = temp_location.rack_pk.manageNum
            temp_subDict['rackLocation'] = temp_location.rackLocation
            rack_list[temp_subDict['rack_pk']].append(temp_subDict)
        temp_subDict['drawIndex'] = int(temp_subDict['rackLocation']) + int(temp_subDict['size']) - 1
    # make server list for rack
    for switch in switch_asset_list:
        temp_subDict = dict()
        temp_subDict['assetNum'] = switch.assetInfo.assetNum
        temp_subDict['manageNum'] = switch.manageNum
        temp_subDict['manageSpec'] = switch.manageSpec
        temp_subDict['ip'] = switch.ip
        temp_subDict['use'] = switch.serviceOn
        temp_subDict['size'] = switch.size
        if (temp_subDict['use'] == True):
            temp_subDict['color'] = '255, 204, 255'
        else:
            temp_subDict['color'] = '255, 255, 204'
        temp_subDict['serviceName'] = ''
        temp = switch.serviceOn
        if (temp == True):
            temp_subDict['onOff'] = 'On'
        else:
            temp_subDict['onOff'] = 'Off'
        temp_location = switch.location
        if temp_location.rack is not None:
            temp_subDict['rack_pk'] = temp_location.rack.manageNum
            temp_subDict['rackLocation'] = temp_location.rackLocation
            rack_list[temp_subDict['rack_pk']].append(temp_subDict)
        temp_subDict['drawIndex'] = int(temp_subDict['rackLocation']) + int(temp_subDict['size']) - 1
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
            position[(inrack['drawIndex']) - 1] = inrack
        data.append({'data': list(reversed(position)), 'rack': rack})
    context['rack_list'] = rack_total
    context['data'] = data
    return render(request, 'dbApp/rack_detail.html', context)


def server_detail(request):
    #############################로그인#############################
    user = getUser(request.session)  # 여기부터 아래까지 총 3줄이 로그인 검증 부분입니당
    if user is None:
        return HttpResponseRedirect('/dbApp/')
    context = {'username': user.first_name}

    #############################로그인#############################
    searchText = request.GET.get("data")
    serverList = Server.objects.filter(Q(manageNum=searchText) | Q(manageSpec=searchText) | Q(ip=searchText))
    if serverList.count() == 0:
        return HttpResponse("찾으시는 제품이 없습니다.")
    server = serverList[0]

    my_prefetch = Prefetch('ss_server', queryset=ServerService.objects.select_related('service'), to_attr="services")
    server_list = Server.objects.select_related('location', 'assetInfo', 'location__rack_pk').prefetch_related(
        my_prefetch).filter(manageNum=server.manageNum)
    server = server_list[0]
    temp_dict = dict()
    temp_dict['assetInfo'] = server.assetInfo
    temp_dict['manageNum'] = server.manageNum
    temp_dict['manageSpec'] = server.manageSpec
    temp_dict['core'] = server.core
    temp_dict['ip'] = server.ip
    if len(server.services) is not 0:
        temp_serverservice = server.services[0]
        temp = temp_serverservice.Use
        if (temp == True):
            temp_dict['use'] = "On"
        else:
            temp_dict['use'] = "Off"
        temp_service = temp_serverservice.service
        temp_dict['serviceName'] = temp_service.serviceName
    temp_location = server.location
    if temp_location.rack_pk is not None:
        temp_dict['location'] = temp_location.rack_pk.location
    else:
        temp_dict['location'] = temp_location.realLocation

    context['server_list'] = temp_dict
    return render(request, 'dbApp/server_detail.html', context)


def switch_detail(request):
    #############################로그인#############################
    user = getUser(request.session)  # 여기부터 아래까지 총 3줄이 로그인 검증 부분입니당
    if user is None:
        return HttpResponseRedirect('/dbApp/')
    context = {'username': user.first_name}

    #############################로그인#############################
    searchText = request.GET.get("data")
    switchList = Switch.objects.filter(Q(manageNum=searchText) | Q(manageSpec=searchText) | Q(ip=searchText))
    if switchList.count() == 0:
        return HttpResponse("찾으시는 제품이 없습니다.")
    switch = switchList[0]

    switch_list = Switch.objects.select_related('location', 'location__rack').filter(manageNum=switch.manageNum)
    switch = switch_list[0]

    temp_dict = {}
    temp_dict['assetInfo'] = switch.assetInfo
    temp_dict['manageNum'] = switch.manageNum
    temp_dict['manageSpec'] = switch.manageSpec
    temp_dict['ip'] = switch.ip
    temp_location = switch.location
    if temp_location.rack is not None:
        temp_dict['location'] = temp_location.rack.location
    else:
        temp_dict['location'] = temp_location.realLocation
    temp = switch.serviceOn
    if (temp == True):
        temp_dict['onOff'] = 'On'
    else:
        temp_dict['onOff'] = 'Off'

    context['switch_list'] = temp_dict
    return render(request, 'dbApp/switch_detail.html', context)


def search_assets(request):
    #############################로그인#############################
    user = getUser(request.session)  # 여기부터 아래까지 총 3줄이 로그인 검증 부분입니당
    if user is None:
        return HttpResponseRedirect('/dbApp/')
    context = {'username': user.first_name}

    #############################로그인#############################

    searchText = request.GET.get("searchText")

    # 에셋 쿼리
    asset_prefetch_server = Prefetch('server', to_attr='servers')
    asset_prefetch_switch = Prefetch('switch', to_attr='switches')
    asset_prefetch_storageasset = Prefetch('storageasset', to_attr='storages')
    asset_prefetch_rack = Prefetch('rack', to_attr='racks')
    asset_total_list = Asset.objects.all().prefetch_related(asset_prefetch_server, asset_prefetch_switch,
                                                            asset_prefetch_storageasset,
                                                            asset_prefetch_rack).filter(
        Q(assetNum__icontains=searchText) | Q(assetName__icontains=searchText) | Q(standard__icontains=searchText) | Q(
            purchaseLocation__icontains=searchText))
    search_asset_list = make_asset_dict_list(asset_total_list)
    context['asset_total_list'] = search_asset_list

    # 서버 쿼리
    server_prefetch_server = Prefetch('ss_server', queryset=ServerService.objects.select_related('service'),
                                      to_attr="services")
    server_asset_num_query = Q(assetInfo__assetNum__icontains=searchText)
    server_manage_num_query = Q(manageNum__icontains=searchText)
    server_manage_spec_query = Q(manageSpec__icontains=searchText)
    server_location_query1 = Q(location__rack_pk__location__icontains=searchText)
    server_location_query2 = Q(location__realLocation__icontains=searchText)
    server_ip_query = Q(ip__icontains=searchText)
    server_search_list = Server.objects.select_related('assetInfo', 'location', 'location__rack_pk').filter(
        server_asset_num_query | server_manage_num_query |
        server_manage_spec_query | server_location_query1 |
        server_location_query2 | server_ip_query
    ).prefetch_related(server_prefetch_server)
    context['server_asset_list'] = make_server_dict_list(server_search_list)

    # 스위치 쿼리
    switch_asset_num_query = Q(assetInfo__assetNum__icontains=searchText)
    switch_manage_num_query = Q(manageNum__icontains=searchText)
    switch_manage_spec_query = Q(manageSpec__icontains=searchText)
    switch_location_query1 = Q(location__rack__location__icontains=searchText)
    switch_location_query2 = Q(location__realLocation__icontains=searchText)
    switch_ip_query = Q(ip__icontains=searchText)
    switch_asset_list = Switch.objects.select_related('assetInfo', 'location', 'location__rack').filter(
        switch_asset_num_query | switch_manage_num_query |
        switch_manage_spec_query | switch_location_query1 |
        switch_location_query2 | switch_ip_query
    )
    context['switch_asset_list'] = make_switch_dict_list(switch_asset_list)

    # 랙 쿼리
    rack_asset_num_query = Q(assetInfo__assetNum__icontains=searchText)
    rack_manage_num_query = Q(manageNum__icontains=searchText)
    rack_manage_spec_query = Q(manageSpec__icontains=searchText)
    rack_location_query = Q(location__icontains=searchText)
    rack_asset_list = Rack.objects.select_related('assetInfo').filter(
        rack_asset_num_query | rack_manage_num_query |
        rack_manage_spec_query | rack_location_query
    )
    context['rack_asset_list'] = make_rack_dict_list(rack_asset_list)
    return render(request, 'dbApp/searchResult.html', context)


def edit_asset(request, asset_num):
    return HttpResponse("자산번호" + asset_num + "를 수정")


def edit_one_asset(request, asset_type, manage_num):
    return HttpResponse("관리번호" + manage_num + "를 수정")


@csrf_exempt
def get_location(request, asset_type, manage_num):
    if asset_type == "server":
        this_server = Server.objects.prefetch_related('location', 'location__rack_pk').get(manageNum=manage_num)
        is_in_rack = (this_server.location.rack_pk is not None)
        if is_in_rack:
            rack_num = this_server.location.rack_pk.manageNum
            rack_idx = this_server.location.rackLocation
            real_location = None
        else:
            rack_num = None
            rack_idx = None
            real_location = this_server.location.realLocation
    elif asset_type == "switch":
        this_switch = Switch.objects.prefetch_related('location', 'location__rack').get(manageNum=manage_num)
        is_in_rack = (this_switch.location.rack is not None)
        if is_in_rack:
            rack_num = this_switch.location.rack.manageNum
            rack_idx = this_switch.location.rackLocation
            real_location = None
        else:
            rack_num = None
            rack_idx = None
            real_location = this_switch.location.realLocation
    temp_dict = dict()
    temp_dict['is_in_rack'] = is_in_rack
    temp_dict['rack_manage_num'] = rack_num
    temp_dict['rack_idx'] = rack_idx
    temp_dict['real_location'] = real_location

    return HttpResponse(json.dumps(temp_dict))


@csrf_exempt
def save_asset(request, asset_num):
    print("save_asset")
    target_asset = Asset.objects.filter(assetNum=asset_num).first()
    target_asset.acquisitionDate = request.POST.get("acquisitionDate")
    target_asset.assetName = request.POST.get("assetName")
    target_asset.standard = request.POST.get("standard")
    target_asset.acquisitionCost = request.POST.get("acquisitionCost")
    target_asset.purchaseLocation = request.POST.get("purchaseLocation")
    target_asset.maintenanceYear = request.POST.get("maintenanceYear")
    target_asset.save()
    return HttpResponse("ok")


@csrf_exempt
def save_new_alloc_size(request, id):
    target_storage_asset = StorageAsset.objects.filter(manageNum=id).first()
    target_storage = Storage.objects.filter(storageAsset=target_storage_asset.id).first()
    target_storage.allocUnitSize = request.POST.get("alloc_size")
    target_storage.save()
    return HttpResponse("ok")


@csrf_exempt
def save_one_asset(request, asset_type, id):
    if asset_type == "server":
        int_rackLocation = request.POST.get("rackLocation")
        str_reallocation = request.POST.get("realLocation")
        rack_managenum = request.POST.get("rack_manage_num")

        my_server = Server.objects.prefetch_related('location', 'location__rack_pk').get(manageNum=id)
        if request.POST.get("isInRack") == "true":
            try:
                rack = Rack.objects.filter(manageNum=rack_managenum)
                if rack.count() == 0:
                    raise Rack.DoesNotExist
            except Rack.DoesNotExist:
                print("NOT SAVED : NO SUCH RACK")
                return HttpResponse("error", status=404)
            try:
                target_rack = rack.first()
                upper_range = int(int_rackLocation) + int(request.POST.get("size"))
                switches_in_rack = SwitchLocation.objects.filter(rack=target_rack.id, rackLocation=int_rackLocation)
                servers_in_rack = ServerLocation.objects.filter(rack_pk=target_rack.id, rackLocation=int_rackLocation)

                if servers_in_rack.count() != 0:
                    print("server is IN_RACK")
                    something = ServerLocation.objects.filter(server_pk=my_server.id)
                    if something.count() == 0:
                        raise Rack.DoesNotExist
                if switches_in_rack.count() != 0:
                    print("switch is IN_RACK")
                    raise Rack.DoesNotExist
            except Rack.DoesNotExist:
                print("NOT SAVED")
                return HttpResponse("error", status=404)
            my_server.isInRack = True
        else:
            my_server.isInRack = False
        my_server.save()
        try:
            temp_rack = Rack.objects.get(manageNum=rack_managenum)
            my_server.location.rack_pk = temp_rack
            my_server.location.rackLocation = int_rackLocation
            my_server.location.realLocation = None
            my_server.location.save()
        except:
            my_server.location.rack_pk = None
            my_server.location.rackLocation = None
            my_server.location.realLocation = str_reallocation
            my_server.location.save()

        target = Server.objects.filter(manageNum=id).first()
        target.manageSpec = request.POST.get("manageSpec")
        target.size = request.POST.get("size")
        target.core = request.POST.get("core")
        target.ip = request.POST.get("ip")
        target.save()
    elif asset_type == "storage":
        target = StorageAsset.objects.filter(manageNum=id).first()
        target.manageSpec = request.POST.get("manageSpec")
        target.location = request.POST.get("location")
        target.standard = request.POST.get("standard")
        target.save()
    elif asset_type == "switch":
        int_rackLocation = request.POST.get("rackLocation")
        str_reallocation = request.POST.get("realLocation")
        rack_managenum = request.POST.get("rack_manage_num")

        my_switch = Switch.objects.prefetch_related('location', 'location__rack').get(manageNum=id)
        if request.POST.get("isInRack") == "true":
            try:
                rack = Rack.objects.filter(manageNum=rack_managenum)
                if rack.count() == 0:
                    raise Rack.DoesNotExist
            except Rack.DoesNotExist:
                print("NOT SAVED : NO SUCH RACK")
                return HttpResponse("error", status=404)
            try:
                target_rack = rack.first()
                switches_in_rack = SwitchLocation.objects.filter(rack=target_rack.id, rackLocation=int_rackLocation)
                servers_in_rack = ServerLocation.objects.filter(rack_pk=target_rack.id, rackLocation=int_rackLocation)
                if servers_in_rack.count() != 0:
                    print("NOT SAVED")
                    raise Rack.DoesNotExist
                if switches_in_rack.count() != 0:
                    print("Something is IN_RACK")
                    something = SwitchLocation.objects.filter(switch=my_switch.id)
                    if something.count() == 0:
                        raise Rack.DoesNotExist
            except Rack.DoesNotExist:
                return HttpResponse("error", status=404)
            my_switch.isInRack = True
        else:
            my_switch.isInRack = False
        my_switch.save()
        try:
            temp_rack = Rack.objects.get(manageNum=rack_managenum)
            my_switch.location.rack = temp_rack
            my_switch.location.rackLocation = int_rackLocation
            my_switch.location.realLocation = None
            my_switch.location.save()
        except:
            my_switch.location.rack = None
            my_switch.location.rackLocation = None
            my_switch.location.realLocation = str_reallocation
            my_switch.location.save()

        target = Switch.objects.filter(manageNum=id).first()
        target.manageSpec = request.POST.get("manageSpec")
        target.size = request.POST.get("size")
        target.ip = request.POST.get("ip")
        if request.POST.get("serviceOn") == "On":
            target.serviceOn = True
        else:
            target.serviceOn = False
        target.save()
    elif asset_type == "rack":
        target = Rack.objects.filter(manageNum=id).first()
        target.manageSpec = request.POST.get("manageSpec")
        target.location = request.POST.get("location")
        target.size = request.POST.get("size")
        target.save()
    elif asset_type == "asset":
        target_asset = Asset.objects.filter(assetNum=id).first()
        target_asset.acquisitionDate = request.POST.get("acquisitionDate")
        target_asset.assetName = request.POST.get("assetName")
        target_asset.standard = request.POST.get("standard")
        target_asset.acquisitionCost = request.POST.get("acquisitionCost")
        target_asset.purchaseLocation = request.POST.get("purchaseLocation")
        target_asset.maintenanceYear = request.POST.get("maintenanceYear")
        target_asset.save()
    return HttpResponse("ok")


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
            if rack.count() == 0:
                raise Rack.DoesNotExist
        except Rack.DoesNotExist:
            return HttpResponse("error", 404)
        rack.delete()
    elif asset_type == "storage":
        try:
            storage = StorageAsset.objects.filter(manageNum=manage_num)
            if storage.count() == 0:
                raise StorageAsset.DoesNotExist
        except StorageAsset.DoesNotExist:
            return HttpResponse("error", 404)
        storage.delete()

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
