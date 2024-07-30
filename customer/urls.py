from django.urls import path
from . import views

urlpatterns = [
    path('', views.show_account,name='account'),
    path('logout', views.signout,name='logout')
]
