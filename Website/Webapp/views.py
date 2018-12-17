from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse

def base(request):
    return render(request, 'Webapp/base.html')
