from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

# home path view
def index(request):
    return HttpResponse('<h1> Hello from FrindLink home page! <h1>')
