from datetime import date
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Prefetch, Q
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from accounts.models import UserProfile
from orders.forms import OrderForm

from .models import Cart
from .context_processors import get_cart_amounts, get_cart_counter
from menu.models import Category, FoodItem, ReviewRating
from vendor.models import AvailableHour, Vendor

def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)

    context = {
        'vendors': vendors,
    }
    return render(request, 'marketplace/listings.html', context)


def vendor_details(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset = FoodItem.objects.filter(is_available=True).prefetch_related(
            'reviewrating_set')  # Prefetch reviews
        )
    )
    # for category in categories:
    #     print(f"Category: {category.category_name}")
    #     for fooditem in category.fooditems.all():
    #         print(f"FoodItem: {fooditem.food_title}")
    #         for review in fooditem.reviewrating_set.all():
    #             print(f"Review by {review.user}: Rating: {review.rating}, Review: {review.review}")
    
    
    available_hours = AvailableHour.objects.filter(vendor=vendor).order_by('day', '-from_hour')

    # get current day
    today_date = date.today()
    today = today_date.isoweekday()
    
    current_day_hours = AvailableHour.objects.filter(vendor=vendor, day=today)
        
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None

    context = {
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items,
        'available_hours': available_hours,
        'current_day_hours': current_day_hours,
    }
    return render(request, 'marketplace/vendor_details.html', context)


def fooditem_details(request, food_id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            fooditem = FoodItem.objects.get(id=food_id)
            print("average", fooditem.averageRating())
            # Get reviews for this food item
            reviews = ReviewRating.objects.filter(fooditem=fooditem, status=True).order_by('-created_at')
            # Build the response data
            reviews_data = []
            for review in reviews:
                user_profile = UserProfile.objects.get(user=review.user)
                reviews_data.append({
                    'profile_picture': user_profile.profile_picture.url,
                    'username': review.user.full_name(),
                    'rating': review.rating,
                    'subject': review.subject,
                    'review': review.review,
                    'date': review.created_at,
                })

            data = {
            'food_image': fooditem.image.url,
            'food_title': fooditem.food_title,
            'description': fooditem.description,
            'average_rating': round(fooditem.averageRating(), 1),
            'review_count': fooditem.countReview(),
            'price': str(fooditem.price),  # Convert Decimal to string for JSON
            'reviews': reviews_data,
            }
            return JsonResponse({'status': 'success', 'data': data})

        except:
            return JsonResponse({'status': 'failed', 'message': 'Fooditem does not exist'})
    
    else:
        return JsonResponse({'status': 'failed', 'message': 'Invalid request'})

def add_to_cart(request, food_id):
    if request.user.is_authenticated:
        # check if the request is made with ajax
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # check if fooditem exists
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                # check if the user has already added that specific food to the cart
                try:
                    checkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    # increase the cart quantity
                    checkCart.quantity += 1
                    checkCart.save()
                    return JsonResponse({'status': 'success', 'message': 'Increased the cart quantity', 'cart_count': get_cart_counter(request), 'qty': checkCart.quantity, 'cart_amounts': get_cart_amounts(request)})
                except:
                    checkCart = Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
                    return JsonResponse({'status': 'success', 'message': 'Added the food to the cart', 'cart_count': get_cart_counter(request), 'qty': checkCart.quantity, 'cart_amounts': get_cart_amounts(request)})
            except:
                return JsonResponse({'status': 'failed', 'message': 'Fooditem does not exist'})
        else:
            return JsonResponse({'status': 'failed', 'message': 'Invalid request'})

    else:
        return JsonResponse({'status': 'login required', 'message': 'You have to login!'})
    


# decrement cart item functionality
def decrement_cart(request, food_id):
    if request.user.is_authenticated:
        # check if the request is made with ajax
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # check if fooditem exists
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                # check if the user has already added that specific food to the cart
                try:
                    checkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    if checkCart.quantity > 1:
                    # decrease the cart quantity
                        checkCart.quantity -= 1
                        checkCart.save()
                    else:
                        checkCart.delete()
                        checkCart.quantity = 0
                    return JsonResponse({'status': 'success', 'cart_count': get_cart_counter(request), 'qty': checkCart.quantity, 'cart_amounts': get_cart_amounts(request)})
                except:
                    return JsonResponse({'status': 'failure', 'message': 'You do not have this item in your cart'})
            except:
                return JsonResponse({'status': 'failure', 'message': 'Fooditem does not exist'})
        else:
            return JsonResponse({'status': 'failure', 'message': 'Invalid request'})

    else:
        return JsonResponse({'status': 'login required', 'message': 'You have to login!'})
    

@login_required(login_url = 'login')
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/cart.html', context)



def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        # check if the request is made with ajax
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                # check if the cart item exists
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status': 'success', 'message': 'Food item has been deleted from cart.', 'cart_count': get_cart_counter(request), 'cart_amounts': get_cart_amounts(request)})
            except:
                return JsonResponse({'status': 'failure', 'message': 'Fooditem does not exist'})
        else:
            return JsonResponse({'status': 'failure', 'message': 'Invalid request!'})
        

@login_required(login_url='login')
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')
    
    user_profile = UserProfile.objects.get(user=request.user)
    default_values = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'phone': request.user.phone_number,
        'email': request.user.email,
        'address': user_profile.address,
        'country': user_profile.country,
        'state': user_profile.state,
        'city': user_profile.city,
        'pin_code': user_profile.pin_code,
    }

    form = OrderForm(initial=default_values)
    context = {
        'form': form,
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/checkout.html', context)


def search(request):
    if 'address' not in request.GET:
        return redirect('marketplace')
    else:
        address = request.GET['address']
        latitude = request.GET['lat']
        longitude = request.GET['lng']
        radius = request.GET['radius']
        keyword = request.GET['keyword']

        # get vendor ids that have the food item user is looking for
        fetch_vendors_by_fooditems = FoodItem.objects.filter(food_title__icontains=keyword, is_available=True).values_list('vendor', flat=True)
        
        vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True))
        if latitude and longitude and radius:
            pnt = GEOSGeometry('POINT(%s %s)' % (longitude, latitude))

            vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True), 
            user_profile__location__distance_lte=(pnt, D(km=radius))
            ).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")

            for v in vendors:
                v.kms = round(v.distance.km, 1)
        context = {
            'vendors': vendors,
            'vendors_count': vendors.count(),
            'source_location': address,
        }

        return render(request, 'marketplace/listings.html', context)