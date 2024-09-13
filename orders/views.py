from datetime import datetime
from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
import simplejson as json

from marketplace.context_processors import get_cart_amounts
from marketplace.models import Cart
from menu.models import FoodItem
from orders.utils import generate_order_number, generate_transaction_id
from accounts.utils import send_notification_email

from .forms import OrderForm
from .models import Order, OrderedFood, Payment

@login_required(login_url='login')
def place_order(request):
    # quering the items in the cart
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    # if the count is equal or less than zero redirect to marketplace page bcs cart is empty
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')
    
    # the id of all the vendors from which fooditems have been added to cart
    vendors_ids = []
    for i in cart_items:
        if i.fooditem.vendor.id not in vendors_ids:
            vendors_ids.append(i.fooditem.vendor.id)

    subtotal = 0
    total_data = {}
    k = {}
    for i in cart_items:
        fooditem = FoodItem.objects.get(pk=i.fooditem.id, vendor_id__in=vendors_ids)
        v_id = fooditem.vendor.id
        if v_id in k:
            subtotal = k[v_id]
            subtotal += (fooditem.price * i.quantity)
            k[v_id] = subtotal
        else:
            subtotal = (fooditem.price * i.quantity)
            k[v_id] = subtotal
        total_data.update({fooditem.vendor.id: str(subtotal)})

    subtotal = get_cart_amounts(request)['subtotal']
    total_tax = get_cart_amounts(request)['tax']
    grand_total = get_cart_amounts(request)['grand_total']

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address = form.cleaned_data['address']
            order.country = form.cleaned_data['country']
            order.state = form.cleaned_data['state']
            order.pin_code = form.cleaned_data['pin_code']
            order.user = request.user
            order.total = grand_total
            order.total_tax = total_tax
            # order.tax_data = json.dumps(tax_data)
            order.tax_data = 0
            order.total_data = json.dumps(total_data)
            order.payment_method = request.POST['payment_method']
            order.save() 
            # order id/pk gets generated after saving
            order.order_number = generate_order_number(order.id)
            order.vendors.add(*vendors_ids)
            order.save() 
            context = {
                'order': order,
                'cart_items': cart_items,
            }
            return render(request, 'orders/place_order.html', context)

        else:
            print(form.errors)
    
    return render(request, 'orders/place_order.html')


@ensure_csrf_cookie
def get_csrf_token(request):
    print('here')
    return JsonResponse({'csrfToken': request.META['CSRF_COOKIE']})


@login_required(login_url='login')
def payments(request):
    # check if the request is ajax
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        # store the payment details in the Payment model
        order_number = request.POST.get('order_number')
        payment_method = request.POST.get('payment_method')
        transaction_id = generate_transaction_id(order_number)

        order = Order.objects.get(user=request.user, order_number=order_number)
        payment = Payment(
            user = request.user,
            transaction_id = transaction_id,
            payment_method = payment_method,
            amount = order.total,
            status = 'successful'
        )
        payment.save()


        # update the Order model
        order.payment = payment
        order.is_ordered = True
        order.save()
        

        # move the cart items into OrderedFood model
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            ordered_food = OrderedFood()
            ordered_food.order = order
            ordered_food.payment = payment
            ordered_food.user = request.user
            ordered_food.fooditem = item.fooditem
            ordered_food.quantity = item.quantity
            ordered_food.price = item.fooditem.price
            ordered_food.amount = item.fooditem.price * item.quantity # total amount
            ordered_food.save()


        # send order confirmation email to the customer
        email_subject = 'Thank you for ordering from us'
        email_template = 'orders/order_confirmation_email.html'

        ordered_food = OrderedFood.objects.filter(order=order)
        customer_subtotal = 0
        for item in ordered_food:
            customer_subtotal += (item.price * item.quantity)
            
        context = {
            'user': request.user,
            'order': order,
            'to_email': order.email,
            'ordered_food': ordered_food,
            'domain': get_current_site(request),
            'customer_subtotal': customer_subtotal,
        }

        send_notification_email(email_subject, email_template, context)
        
        

        # send order received email to vendor
        email_subject = 'You have received a new order.'
        email_template = 'orders/new_order_received.html'
        to_emails = []
        for i in cart_items:
            if i.fooditem.vendor.user.email not in to_emails:
                to_emails.append(i.fooditem.vendor.user.email)
        print(to_emails)
        context = {
            'order': order,
            'to_email': to_emails,
        }
        send_notification_email(email_subject, email_template, context)
        

        # clear the cart if the payment is a success
        cart_items.delete()

        # return to ajax with the status success or failure
        response = {
            'order_number': order_number,
            'transaction_id': transaction_id,
        }
        return JsonResponse(response)

    return HttpResponse('Payments view')


def order_complete(request):
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')

    try:
        order = Order.objects.get(order_number=order_number, payment__transaction_id=transaction_id, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order)

        subtotal = 0
        for item in ordered_food:
            subtotal+= (item.price * item.quantity)
            
        # tax_data = json.loads(order.tax_data)

        context = {
            'order': order,
            'ordered_food': ordered_food,
            'subtotal': subtotal,
        }
 
        return render(request, 'orders/order_complete.html', context)
    except:
        return redirect('home')
    