from django.urls import path
from . import views

urlpatterns = [
    path('registerUser', views.registerUser, name='registerUser'),
    path('registerVendor', views.registerVendor, name='registerVendor'),

    path('myAccount/', views.myAccount, name='myAccount'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('vendorDashboard/', views.vendorDashboard, name='vendorDashboard'),
    path('custDashboard/', views.custDashboard, name='custDashboard'),


]