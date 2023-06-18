from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('iim/', views.iim, name='iim'),
    path('mrnn/', views.mrnn, name='mrnn'),
]