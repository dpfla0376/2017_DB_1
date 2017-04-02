from django.shortcuts import render
from dbApp.models import Asset

# Create your views here.

def asset_total(request):
    return render(request, 'dbApp/asset_total.html', {})
