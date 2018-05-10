from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('doPost/', views.doPost, name='doPost'),
]