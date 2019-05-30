from django.http import HttpResponse
from django.shortcuts import render

def hello(request):
    context = {}
    context['hello'] = 'hello world i am your father'
    return render(request,'hello.html',context)