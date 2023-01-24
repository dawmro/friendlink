from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

# home path view
def index(request):
    return render(request, 'index.html')

# signup view
def signup(request):
    return render(request, 'signup.html')

