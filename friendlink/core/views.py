from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

# home path view
def index(request):
    return render(request, 'index.html')

# signup view
def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
    else
        return render(request, 'signup.html')

