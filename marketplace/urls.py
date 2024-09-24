from django.urls import path
from . import views


urlpatterns = [
    path('', views.marketplace, name='marketplace'),
    path('<slug:vendor_slug>/', views.vendor_details, name='vendor_details'),
    path('fooditem-details/<int:food_id>/', views.fooditem_details, name='fooditem_details'),
    # ADD ITEM TO CART
    path('add_to_cart/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    # DECREMENT CART ITEM
    path('decrement_cart/<int:food_id>/', views.decrement_cart, name='decrement_cart'),
    # DELETE CART ITEM
    path('delete_cart/<int:cart_id>', views.delete_cart, name="delete_cart"),
    

]