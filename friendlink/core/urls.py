from django.urls import path
from . import views

urlpatterns = [
    # home path
    path('', views.index, name='index')
]
