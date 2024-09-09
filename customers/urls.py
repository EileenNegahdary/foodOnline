from accounts import views as AccountViews
from . import views

from django.urls import path


urlpatterns = [
    path('', AccountViews.custDashboard, name='customer'),
    path('profile/', views.cprofile, name='cprofile'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('order_detail/<int:order_number>/', views.order_detail, name='order_detail'),
]