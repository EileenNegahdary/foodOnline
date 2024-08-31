from django.urls import path, include
from . import views
from accounts import views as AccountViews

urlpatterns = [
    path('', AccountViews.vendorDashboard, name='vendor'),
    path('profile', views.vendor_profile, name='vendor_profile'),
    path('menu-builder', views.menu_builder, name='menu_builder'),
    path('menu-builder/category/<int:pk>', views.fooditems_by_category, name='fooditems_by_category'),

    # CRUD Category
    path('menu-builder/category/add', views.add_category, name='add_category'),
    path('menu-builder/category/edit/<int:pk>', views.edit_category, name='edit_category'),
    path('menu-builder/category/delete/<int:pk>', views.delete_category, name='delete_category'),

    # CRUD Fooditems
    path('menu-builder/food/add', views.add_food, name='add_food'),
    path('menu-builder/food/edit/<int:pk>', views.edit_food, name='edit_food'),
    path('menu-builder/food/delete/<int:pk>', views.edit_food, name='delete_food'),

    # Available Hours CRUD
    path('available-hours', views.available_hours, name='available_hours'),
    path('available-hours/add/', views.add_available_hours, name='add_available_hours'),
    path('available-hours/remove/<int:pk>/', views.remove_available_hour, name='remove_available_hour'),
    
]
