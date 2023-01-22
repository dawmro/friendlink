from django.urls import path

urlpatterns = [
    # home path
    path('', views.index, name=index)
]
]