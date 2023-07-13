from django.urls import path

from . import views

urlpatterns = [
    # path("", views.index, name="index"),
    path('fetchData/', views.fetch_data, name='fetchData'),
    path('cdrec/', views.cdrec, name='cdrec'),
    path('iim/', views.iim, name='iim'),
    path('mrnn/', views.mrnn, name='mrnn'),
    path('stmvl/', views.stmvl, name='stmvl'),
    path('optimization/cdrec/', views.cdrec_optimization, name='cdrec_optimization'),
    path('optimization/iim/', views.iim_optimization, name='iim_optimization'),
    path('optimization/mrnn/', views.mrnn_optimization, name='mrnn_optimization'),
    path('optimization/stmvl/', views.stmvl_optimization, name='stmvl_optimization'),
]