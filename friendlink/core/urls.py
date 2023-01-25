from django.urls import path
from . import views

urlpatterns = [
    # home path
    path('', views.index, name='index'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin')
]
