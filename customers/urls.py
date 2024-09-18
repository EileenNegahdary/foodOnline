from accounts import views as AccountViews
from . import views

from django.urls import path


urlpatterns = [
    path('', AccountViews.custDashboard, name='customer'),
    path('profile/', views.cprofile, name='cprofile'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('order_detail/<int:order_number>/', views.order_detail, name='order_detail'),
    path('receive_order/<int:order_number>/', views.receive_order, name='receive_order'),
    # path('get_review_form/<int:order_number>/', views.get_review_form, name='get_review_form'),
    # rate and review page
    path('rate/<int:order_number>/', views.rate, name='rate'),
    # to submit review
    path('submit_review/<int:fooditem_id>', views.submit_review, name='submit_review'),
]