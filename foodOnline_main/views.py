from django.http import request
from django.shortcuts import render

from django.db.models import Q
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance

from vendor.models import Vendor
from .utils import get_or_set_current_location
    
def home(request):
    if get_or_set_current_location(request) is not None:
        
        pnt = GEOSGeometry('POINT(%s %s)' % (get_or_set_current_location(request)))

        vendors = Vendor.objects.filter(user_profile__location__distance_lte=(pnt, D(km=100))).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")

        for v in vendors:
            v.kms = round(v.distance.km, 1)

    else:
        vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]
        
    context = {
        'vendors': vendors,
    }
    return render(request, 'home.html', context)