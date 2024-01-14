from datetime import datetime
from django.shortcuts import get_object_or_404, render , redirect
from decimal import Decimal
from orders.models import Order, OrderProduct, Wallet, WalletTransaction 
from .forms import RegistrationForm, UserForm, UserProfileCreateForm, UserProfileForm, WalletForm
from .models import Account, UserProfile
from django.contrib import messages , auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.db.models import Q

import random
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password

from carts.views import _cart_id
from carts.models import Cart, CartItem
# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        profile_form = UserProfileForm(request.POST) 
        if form.is_valid() and profile_form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()

            # Create a user profile
            profile = UserProfile()
            profile.user_id = user.id
            profile.profile_picture = 'default/default-user.png'
            address_line_1 = profile_form.cleaned_data['address_line_1']
            address_line_2 = profile_form.cleaned_data['address_line_2']
            profile.address_line_1 = address_line_1
            profile.address_line_2 = address_line_2
            city = profile_form.cleaned_data['city']
            state = profile_form.cleaned_data['state']
            country = profile_form.cleaned_data['country']
            profile.country = country
            profile.state = state
            profile.city = city
            profile.is_flagged = True
            profile.save()

             # USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request,"We have sent you a verification email to your email address. Please verify it")
            return redirect('/accounts/login/?command=verification&email='+email)

    else:
        form = RegistrationForm()
        profile_form = UserProfileForm()
        
    context = {
        'form': form,
        'profile_form':profile_form
    }
    return render(request, 'accounts/register.html',context)

def login(request):
     if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password ,is_active = True)
        
        if user is not None and user.user_type == "Admin":
            print(user.user_type)
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('admindashboard')
        elif user is not None and user.user_type == "User":
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    # Get the cart items from the user to access his product variations
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
                    
                    # for item in cart_item:
                    #     item.user = user
                    #     item.save()

            except:
                pass
            request.session["email"]=email
            request.session['password'] = password
            send_otp(request)
            return render(request,'accounts/otp.html',{"email":email})
            # auth.login(request, user)
            # messages.success(request, 'You are now logged in.')
            # return redirect('dashboard')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')

     return render(request, 'accounts/login.html')


def send_otp(request):
    s=""
    for x in range(0,4):
        s+=str(random.randint(0,9))
    request.session["otp"]=s
    send_mail("otp for sign up",s,'ajayjoy618@gmail.com',[request.session['email']],fail_silently=False)
    return render(request,'accounts/otp.html')


def  otp_verification(request):
    if  request.method=='POST':
        otp_=request.POST.get("otp")
    if otp_ == request.session["otp"]:
        # encryptedpassword=make_password(request.session['password'])
        # nameuser=Account(first_name=request.session['first_name'],last_name=request.session['last_name'],email=request.session['email'],password=encryptedpassword)
        # nameuser.save()
        # messages.info(request,'signed in successfully...')
        # Account.is_active=True
        # return redirect('home')
        # user = auth.authenticate(email=email, password=password ,is_active = True)
        email = request.session.get('email')
        password = request.session.get('password')
        user = auth.authenticate(email=email, password=password ,is_active = True)
        auth.login(request, user)
        messages.success(request, 'You are now logged in.')
        return redirect('cart')
    else:
        messages.error(request, 'Invalid OTP')
        return redirect('login')
    

@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')

@login_required(login_url = 'login')
def dashboard(request):
    orders = Order.objects.filter(user=request.user).exclude(status='New', is_ordered=False).order_by('-created_at')
    orders_count = orders.count()

    userprofile = UserProfile.objects.get(user_id=request.user.id, is_flagged = True)
    context = {
        'orders_count': orders_count,
        'userprofile':userprofile
    }
    return render(request, 'accounts/dashboard.html',context)

def activate(request,uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')
    

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # Reset password email
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')

def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('login')
    

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')
    else:
        return render(request, 'accounts/resetPassword.html')
    

@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user).exclude(status='New', is_ordered=False).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/my_orders.html', context)

@login_required(login_url='login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity

    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    }
    return render(request, 'accounts/order_detail.html', context)


@login_required(login_url='login')
def edit_profile(request):
    userprofile = UserProfile.objects.get(user=request.user, is_flagged = True)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/edit_profile.html', context)


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # auth.logout(request)
                messages.success(request, 'Password updated successfully.')
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('change_password')
    return render(request, 'accounts/change_password.html')

@login_required(login_url='login')
def multiple_address(request):
    userprofile = UserProfile.objects.filter(user=request.user)
    # print(userprofile )
    context = {
        'userprofiles' : userprofile
    }
    return render(request, 'accounts/multiple_address.html',context)

@login_required(login_url='login')
def multiple_address_update(request,useprofile_id):
    userprofiles = UserProfile.objects.filter(user=request.user)
    print(useprofile_id)
    for userprofile in userprofiles:
        if userprofile.id == useprofile_id:
            # print(userprofile.id)
            userprofile.is_flagged = True
            userprofile.save()
        else:
            userprofile.is_flagged = False
            userprofile.save()
    return render(request, 'accounts/multiple_address.html' )

@login_required(login_url='login')
def add_new_address(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save(commit=False)  
            user_profile.user = request.user 
            user_profile.save() 
            messages.success(request, 'New address to the user is added!')
            return redirect('add_new_address')
    else:
        form = UserProfileForm()
    return render(request, 'accounts/add_new_address.html',{'form': form})

@login_required(login_url='login')
def orderCancel(request , order_number):
    order = Order.objects.get(order_number=order_number)
    print(order.payment.payment_method)
    if order.payment.payment_method == 'Wallet':
        print("Wallet refund")
        wallet = Wallet.objects.get(user=request.user)
        order_total_decimal = Decimal(str(order.order_total))
        new_balance = order_total_decimal + wallet.balance
        wallet.balance = new_balance
        wallet.save()

        new_transaction = WalletTransaction.objects.create(
            user_id=request.user.id,  
            amount=order_total_decimal,  
            transaction_type='refund',
            timestamp=datetime.now()  # Set the timestamp
        )

        new_transaction.save()

        order.status = 'Cancelled'
        order.is_ordered = False
        order.save()
        messages.success(request, 'Money refunded to your wallet!')
        return redirect('my_orders')
    else:
        order.status = 'Cancelled'
        order.is_ordered = False
        order.save()
    return redirect('my_orders')
