from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, request, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.defaultfilters import slugify

from accounts.views import check_role_vendor
from accounts.models import UserProfile
from accounts.forms import UserProfileForm

from menu.forms import CategoryForm, FoodItemForm
from menu.models import Category, FoodItem

from .models import AvailableHour, Vendor
from .forms import AvailableHourForm, VendorForm
from .utils import get_vendor

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


def menu_builder(request):
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor).order_by('created_at')
    context = {
        'categories': categories,
    }
    return render(request, 'vendor/menu_builder.html', context)


def fooditems_by_category(request, pk=None):
    vendor = get_vendor(request)
    category = get_object_or_404(Category, pk=pk)
    fooditems = FoodItem.objects.filter(vendor=vendor, category=category)
    context = {
        'category': category,
        'fooditems': fooditems,
    }
    return render(request, 'vendor/fooditems_by_category.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            form.save()
            messages.success(request, 'Category added successfully!')
            return redirect('menu_builder')
        
    else:
        form = CategoryForm()
    context = {
        "form": form,
    }
    return render(request, 'vendor/add_category.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            form.save()
            messages.success(request, 'Category Updated successfully!')
            return redirect('menu_builder')
        
    else:
        form = CategoryForm(instance=category)
    context = {
        "form": form,
        'category': category,
    }
    return render(request, 'vendor/edit_category.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, 'Category deleted successfully.')
    return redirect('menu_builder')


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_food(request):
    if request.method  == 'POST':
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            food_item = form.save(commit=False)
            food_item.vendor = get_vendor(request)
            food_item.slug = slugify(food_title)
            form.save()
            messages.success(request, 'Food Item added successfully!')
            return redirect('fooditems_by_category', food_item.category.id)

    else:
        form = FoodItemForm()
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
 
    context = {
        'form': form,
    }

    return render(request, 'vendor/add_food.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_food(request, pk=None):
    food_item = get_object_or_404(FoodItem, pk=pk)
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES, instance=food_item)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            food_item = form.save(commit=False)
            food_item.vendor = get_vendor(request)
            food_item.slug = slugify(food_title)
            form.save()
            messages.success(request, 'Food Item Updated successfully!')
            return redirect('fooditems_by_category', food_item.category.id)
    else:
        form = FoodItemForm(instance=food_item)
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))

    context = {
        'form': form,
        'food': food_item,
    }

    return render(request, 'vendor/edit_food.html', context)


def delete_food(request, pk=None):
    food_item = get_object_or_404(FoodItem, pk=pk)
    food_item.delete()
    messages.success(request, 'Food Item deleted successfully!')
    return redirect('fooditems_by_category', food_item.category.id)



def available_hours(request):
    available_hours = AvailableHour.objects.filter(vendor=get_vendor(request))
    form = AvailableHourForm()
    context = {
        'available_hours': available_hours,
        'form': form,
    }
    return render(request, 'vendor/available-hours.html', context)


def add_available_hours(request):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
            day = request.POST.get('day')
            from_hour = request.POST.get('from_hour')
            to_hour = request.POST.get('to_hour')
            is_closed = request.POST.get('is_closed')
            try:
                hour = AvailableHour.objects.create(vendor=get_vendor(request), day=day, from_hour=from_hour, to_hour=to_hour, is_closed=is_closed)
                if hour:
                    day = AvailableHour.objects.get(id=hour.id)
                    if day.is_closed:
                        response = {'status': 'success', 'id': hour.id, 'day': day.get_day_display(), 'is_closed': 'Closed'}
                    else:
                        response = {'status': 'success', 'id': hour.id, 'day': day.get_day_display(), 'from_hour': hour.from_hour, 'to_hour': hour.to_hour}
                                                
                
                return JsonResponse(response)
            except IntegrityError as e:
                response = {'status':'failure', 'message': f'{from_hour} - {to_hour} already exists for this day', 'error': str(e)}
                return JsonResponse(response)
        else:
            HttpResponse('invalid request')


def remove_available_hour(request, pk=None):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            hour = get_object_or_404(AvailableHour, pk=pk)
            hour.delete()
            print('deleted')
            return JsonResponse({'status': 'success', 'id': pk})
        
     

