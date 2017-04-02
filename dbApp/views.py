from django.shortcuts import render
from dbApp.models import Asset

# Create your views here.

def asset_total(request):
    asset_total_list = Asset.objects.all()
    context = {'asset_total_list': asset_total_list}
    return render(request, 'dbApp/asset_total.html', context)

<<<<<<< HEAD
def server_asset(request):
    server_asset_list = Asset.objects.all()
    context = {'server_asset_list': server_asset_list}
    return render(request, 'dbApp/server_asset.html', context)
=======
def service_resources(request):
    return render(request, 'dbApp/service_resources.html', {});
>>>>>>> 286f7cdb78193ed30933aef15a08097916dd214b
