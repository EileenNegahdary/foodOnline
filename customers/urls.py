from accounts import views as AccountViews
from . import views

from django.urls import path


urlpatterns = [
    path('', AccountViews.custDashboard, name='customer'),
    path('profile/', views.cprofile, name='cprofile'),
]