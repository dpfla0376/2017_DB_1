from django.shortcuts import render
from dbApp.models import Asset

# Create your views here.

def asset_total(request):
    asset_total_list = Asset.objects.all()
    context = {'asset_total_list': asset_total_list}
    return render(request, 'dbApp/asset_total.html', context)
