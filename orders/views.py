import json
from django.core.mail import EmailMessage
import uuid
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
import datetime
from django.contrib import messages
from accounts.forms import WalletForm
from decimal import Decimal 

from store.models import Product
from .models import Coupon, Order, OrderProduct, Payment, Wallet, WalletTransaction
from carts.models import CartItem
from orders.forms import CouponApplyForm, OrderForm
from django.template.loader import render_to_string

# Create your views here.
# def payments(request):
#     return render(request, 'orders/payments.html')

def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])
    
    print(body)
    # Store transaction details inside Payment model
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.status = 'Completed'
    order.save()

    if 'order_number' in request.session:
        del request.session['order_number']

    # Move the cart items to Order Product table
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()


        # Reduce the quantity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    # Send order recieved email to customer
    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/order_recieved_email.html', {
        'user': request.user,
        'order': order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    # Send order number and transaction id back to sendData method via JsonResponse
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)


def cashondelivery(request):
    print(CartItem.objects.filter(user=request.user))
    if CartItem.objects.filter(user=request.user):
        current_user = request.user
        payment_method = 'COD'
        status = 'Accepted'
        payment_id = uuid.uuid4()
        order = Order.objects.filter(user=current_user).last()
        order.is_ordered = True
        amount_paid = order.order_total

        payment = Payment(user=current_user ,payment_id=payment_id ,payment_method=payment_method , amount_paid =amount_paid ,status=status)
        payment.save()
        order.payment = payment
        order.status = 'Accepted'
        order.save()

        if 'order_number' in request.session:
            del request.session['order_number']

        # Move the cart items to Order Product table
        # pay = Payment.objects.get(payment_id=payment_id)
        cart_items = CartItem.objects.filter(user=request.user)

        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order_id = order.id
            orderproduct.payment = payment
            orderproduct.user_id = request.user.id
            orderproduct.product_id = item.product_id
            orderproduct.quantity = item.quantity
            orderproduct.product_price = item.product.price
            orderproduct.ordered = True
            orderproduct.save()

            cart_item = CartItem.objects.get(id=item.id)
            product_variation = cart_item.variations.all()
            orderproduct = OrderProduct.objects.get(id=orderproduct.id)
            orderproduct.variations.set(product_variation)
            orderproduct.save()

            # Reduce the quantity of the sold products
            product = Product.objects.get(id=item.product_id)
            product.stock -= item.quantity
            product.save()

        # Clear cart
        CartItem.objects.filter(user=request.user).delete()

        # Send order recieved email to customer
        mail_subject = 'Thank you for your order!'
        message = render_to_string('orders/order_recieved_email.html', {
            'user': request.user,
            'order': order,
        })
        to_email = request.user.email
        send_email = EmailMessage(mail_subject, message, to=[to_email])
        send_email.send()

        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        context = {
                    'order': order,
                    'payment' : payment,
                    'payment_id': payment_id,
                    'ordered_products': ordered_products
                }
        # request.session['view_executed'] = True    
        return render(request, 'orders/order_complete_cod.html',context)
    else:
        return redirect('home')


def place_order(request, total=0, quantity=0):
    current_user = request.user
    coupon_applied = False

     # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = total + tax
    
    if request.method == 'POST':
         form = OrderForm(request.POST)
         if form.is_valid():
            # Store all the billing information inside Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

             # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #20231212
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            request.session['order_number'] = data.order_number

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
                'coupon_applied' : coupon_applied,
                
            }
            return render(request, 'orders/payments.html', context)

    else:
        order_number = request.session.get('order_number')
        try:
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            tax = order.tax
            grand_total = order.order_total
            total = grand_total - tax
            if order.coupon_applied:
                coupon_applied = True
                
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
                'coupon_applied' :coupon_applied,
                
            }
            return render(request, 'orders/payments.html', context)
        except Order.DoesNotExist:
            return redirect('checkout')        
    
def coupon_apply(request):
    current_user = request.user
    if request.method == 'POST':
        input_value = request.POST.get('couponcode')
        grand_total = request.POST.get('total_price')
        total = request.POST.get('total')
        order_numb = request.POST.get('order_number')
        valid_coupon = Coupon.objects.filter(code=input_value,active=True, valid_from__lte=timezone.now(), valid_to__gte=timezone.now())
        if input_value and valid_coupon:
            order = Order.objects.get(user=current_user, is_ordered=False,order_number=order_numb)
            coupon = get_object_or_404(Coupon, code=input_value)
            discount = coupon.discount
            discount_price =(float(grand_total) * float(discount))/100
            New_Total = float(grand_total)-discount_price

            cart_items = CartItem.objects.filter(user=current_user)
    
            grand_total = 0
            tax = 0
            tax = (2 * New_Total)/100
            grand_total = New_Total + tax
            
            order.order_total="{:.2f}".format(grand_total)
            order.tax = "{:.2f}".format(tax)
            order.coupon_applied = True
            order.save()

            coupon_applied= True
            messages.success(request,f"{discount}% discount on Coupon {input_value}")
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': New_Total,
                'tax': tax,
                'grand_total': grand_total,
                'coupon_applied':coupon_applied,
            }
            return render(request, 'orders/payments.html', context)
        else:
            order = Order.objects.get(user=current_user, is_ordered=False,order_number=order_numb)
            cart_items = CartItem.objects.filter(user=current_user)
    
            tax = (2 * float(total))/100
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            messages.error(request, 'Invalid or Expired Coupon!')
            return render(request, 'orders/payments.html', context)
    
         
def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
    
def debit_wallet(user, amount):
    user_wallet = Wallet.objects.get(user=user)
    if user_wallet.balance >= Decimal(amount):
        user_wallet.balance -= Decimal(amount)
        user_wallet.save()
        WalletTransaction.objects.create(user=user, amount=amount, transaction_type='debit')
        return True  # Transaction successful
    return False  # Insufficient balance
    
def walletPay(request):
    current_user = request.user
    order = Order.objects.filter(user=current_user).last()
    amount_paid = order.order_total
    if debit_wallet(current_user , amount_paid):
        order_number = request.session.get('order_number')    
        if CartItem.objects.filter(user=request.user):
            current_user = request.user
            payment_method = 'Wallet'
            status = 'Accepted'
            payment_id = uuid.uuid4()
            order = Order.objects.filter(user=current_user).last()
            order.is_ordered = True
            amount_paid = order.order_total

        payment = Payment(user=current_user ,payment_id=payment_id ,payment_method=payment_method , amount_paid =amount_paid ,status=status)
        payment.save()
        order.payment = payment
        order.status = 'Accepted'
        order.save()

        if 'order_number' in request.session:
            del request.session['order_number']

        # Move the cart items to Order Product table
        # pay = Payment.objects.get(payment_id=payment_id)
        cart_items = CartItem.objects.filter(user=request.user)

        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order_id = order.id
            orderproduct.payment = payment
            orderproduct.user_id = request.user.id
            orderproduct.product_id = item.product_id
            orderproduct.quantity = item.quantity
            orderproduct.product_price = item.product.price
            orderproduct.ordered = True
            orderproduct.save()

            cart_item = CartItem.objects.get(id=item.id)
            product_variation = cart_item.variations.all()
            orderproduct = OrderProduct.objects.get(id=orderproduct.id)
            orderproduct.variations.set(product_variation)
            orderproduct.save()

            # Reduce the quantity of the sold products
            product = Product.objects.get(id=item.product_id)
            product.stock -= item.quantity
            product.save()

        # Clear cart
        CartItem.objects.filter(user=request.user).delete()

        # Send order recieved email to customer
        mail_subject = 'Thank you for your order!'
        message = render_to_string('orders/order_recieved_email.html', {
            'user': request.user,
            'order': order,
        })
        to_email = request.user.email
        send_email = EmailMessage(mail_subject, message, to=[to_email])
        send_email.send()

        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        context = {
                    'order': order,
                    'payment' : payment,
                    'payment_id': payment_id,
                    'ordered_products': ordered_products
                }
        # request.session['view_executed'] = True    
        return render(request, 'orders/order_complete_cod.html',context)
        #Transaction successfull
    else:
        messages.error(request, 'Insufficient wallet Balance....Add more money to wallet!')
        return redirect('my_wallet')