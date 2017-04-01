from django.shortcuts import render

# Create your views here.

def asset_total(request):
    return render(request, 'asset_total.html', {})
