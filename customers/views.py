from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounts.forms import UserInfoForm, UserProfileForm
from accounts.models import UserProfile
from menu.forms import ReviewForm
from menu.models import FoodItem, ReviewRating
from orders.models import Order, OrderedFood


@login_required(login_url='login')
def cprofile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserInfoForm(request.POST, instance=request.user)
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, 'Profile Updated')
            return redirect('cprofile')
        else:
            print(profile_form.errors)
            print(user_form.errors)
    else:
        profile_form = UserProfileForm(instance=profile)
        user_form = UserInfoForm(instance=request.user)

    context = {
        'profile': profile,
        'profile_form': profile_form,
        'user_form': user_form,
    }
    return render(request, 'customer/cprofile.html', context)


def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')

    context = {
        'orders': orders,
    }
    return render(request, 'customer/my_orders.html', context)



def order_detail(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order)
        subtotal = 0
        for item in ordered_food:
            subtotal += (item.price * item.quantity)

        # tax_data = json.loads(order.tax_data)

        context = {
            'order': order,
            'ordered_food': ordered_food,
            'subtotal': subtotal,
        }
        return render(request, 'customer/order_detail.html', context)
    except:
        return redirect('customer')
    

def receive_order(request, order_number):
    order = Order.objects.get(order_number=order_number)
    order.status = 'Received'
    order.save()
    messages.success(request, 'Order Marked As Received')
    return redirect('customer')


def rate(request, order_number):
    order = Order.objects.get(order_number=order_number)
    ordered_foods = OrderedFood.objects.filter(order=order)
    form = ReviewForm()

    context = {
        'order': order,
        'ordered_foods': ordered_foods,
        'form': form,
    }
    return render(request, 'customer/rate.html', context)

def submit_review(request, fooditem_id):
    print(fooditem_id)
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                fooditem = FoodItem.objects.get(id=fooditem_id)
                order_number = request.POST.get('order_number')
                print(order_number)
                print(fooditem)
                print(request.POST.get('subject'))
                print(request.POST.get('review'))
                print(request.POST.get(f'rating'))
                try:                    
                    print("are we even here")
                    review = ReviewRating.objects.get(user=request.user, fooditem=fooditem, order_number=order_number)
                    print('after reviww')
                    print(review)
                    form = ReviewForm(request.POST, instance=review)
                    print(form)
                    form.save()
                    message = 'Thank you! Your review has been updated'
                    
                except ReviewRating.DoesNotExist:
                    print("or here")
                    print(request.POST)
                    form = ReviewForm(request.POST)
                    print(form)
                    
                    if form.is_valid():
                        print('here??')
                        data = ReviewRating()
                        data.user = request.user
                        data.fooditem = fooditem
                        data.subject = form.cleaned_data['subject']
                        data.rating = form.cleaned_data['rating']
                        data.review = form.cleaned_data['review']
                        data.order_number = form.cleaned_data['order_number']
                        data.ip = request.META.get('REMOTE_ADDR') 
                        data.save()
                        message = 'Thank you! Your review has been submitted'
                    else:
                        print(form.errors)
                
                return JsonResponse({'status': 'success', 'message': message})
                        
            except:
                return JsonResponse({'status': 'failed', 'message': 'Fooditem does not exist'})
            
        else:
            return JsonResponse({'status': 'failed', 'message': 'Invalid request'})
    else:
        return JsonResponse({'status': 'login required', 'message': 'You have to login!'})
    

    




# def get_review_form(request, order_number):
#     if request.user.is_authenticated:
#         # check if the request is made with ajax
#         if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             # check if fooditem exists
#             try:
#                 order = Order.objects.get(order_number=order_number)
#                 ordered_foods = OrderedFood.objects.filter(order=order)
#             except:
#                 return JsonResponse({'status': 'failed', 'message': 'Order Not Found'})
#         else:
#             return JsonResponse({'status': 'failed', 'message': 'Invalid request'})

#     else:
#         return JsonResponse({'status': 'login required', 'message': 'You have to login!'})