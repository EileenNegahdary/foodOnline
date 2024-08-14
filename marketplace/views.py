from django.shortcuts import get_object_or_404, render
from django.db.models import Prefetch
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from .models import Cart
from .context_processors import get_cart_amounts, get_cart_counter
from menu.models import Category, FoodItem
from vendor.models import Vendor

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
            queryset = FoodItem.objects.filter(is_available=True)
        )
    )

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None

    context = {
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/vendor_details.html', context)


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
    cart_items = Cart.objects.filter(user=request.user)
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