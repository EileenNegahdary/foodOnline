from django.shortcuts import render
from django.http import request, HttpResponse

# Create your views here.
def vendor_profile(request):
    return render(request, 'vendor/vendor_profile.html')