from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('submit-name/', views.submit_name, name='submit-name'),
]