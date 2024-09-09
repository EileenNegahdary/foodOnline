from django.urls import path

from . import views

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    path('get-csrf-token/', views.get_csrf_token, name='get_csrf_token'),
    path('payments/', views.payments, name='payments'),
    path('order_complete/', views.order_complete, name='order_complete'),
]
