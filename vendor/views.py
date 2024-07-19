from django.shortcuts import render, get_object_or_404, redirect
from django.http import request, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

from accounts.views import check_role_vendor
from accounts.models import UserProfile
from accounts.forms import UserProfileForm
from vendor.models import Vendor
from vendor.forms import VendorForm

# handling vendor my restaurant section in dashboard
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendor_profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)

        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, 'Settings updated.')
            return redirect('vendor_profile')

        else:
            print(profile_form.errors)
            print(vendor_form.errors)
    
    else:
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)

    context = {
        'profile': profile,
        'vendor': vendor,
        'profile_form': profile_form,
        'vendor_form': vendor_form,
    }
    return render(request, 'vendor/vendor_profile.html', context)