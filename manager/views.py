from django.shortcuts import redirect, render
from django.db.models import Sum
from accounts.models import Account
from category.models import Category
from manager.forms import CategoryForm, CouponForm, ProductForm, UserForm
from orders.models import Coupon, Order, OrderProduct, Payment, Wallet, WalletTransaction
from store.models import Product, ReviewRating
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required(login_url = 'login')
def admindashboard(request):
    sum_of_payment = Payment.objects.aggregate(total=Sum('amount_paid'))
    total_sum = sum_of_payment['total']
    total_sum_trim ="{:.2f}".format(total_sum)
    orders = Order.objects.all().order_by('-order_number')
    total_order = Order.objects.count()
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    paginator = Paginator(orders, 20)
    page = request.GET.get('page')
    paged_orders = paginator.get_page(page)

    context = {
     'orders': paged_orders,
     'total_sum' : total_sum_trim,
     'total_order':total_order,
     'total_products' : total_products,
     'total_categories':total_categories
     }

    return render(request,'manager/dashboard.html',context)

def addProduct(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('productList')
    else:
        form = ProductForm()
    return render(request,'manager/add_product.html',{'form': form})

def addCategory(request):
    if request.method == 'POST':
         form = CategoryForm(request.POST, request.FILES)
         if form.is_valid():
            form.save()
            return redirect('categoryList')
    else:
        form = CategoryForm()
    return render(request,'manager/add_category.html',{'form': form})

def productList(request):
    products = Product.objects.all().order_by('-created_date')
    paginator = Paginator(products, 7)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    context = {
     'products': paged_products,
     }
    return render(request,'manager/product_list.html',context)

def categoryList(request):
    category = Category.objects.all().order_by('category_name')
    paginator = Paginator(category, 7)
    page = request.GET.get('page')
    paged_category = paginator.get_page(page)
    context = {
     'categories': paged_category,
     }
    return render(request,'manager/category_list.html',context)


def editProduct(request, pk):

    product = Product.objects.get(id=pk)
    form = ProductForm(instance=product)

    if request.method == 'POST':
        form = ProductForm(request.POST , request.FILES, instance=product)

        if form.is_valid():
            form.save()
            return redirect('productList')

    context = {

    'product': product,

    'form': form,

    }
    return render(request,'manager/product_edit.html',context)

def editCategory(request , pk):
    category = Category.objects.get(id=pk)
    form = CategoryForm(instance=category)

    if request.method == 'POST':
        form = CategoryForm(request.POST , request.FILES, instance=category)

        if form.is_valid():
            form.save()
            return redirect('categoryList')

    context = {

    'category': category,

    'form': form,

    }
    return render(request,'manager/product_edit.html',context)


def deleteProduct(request, pk):
    product = Product.objects.get(id=pk)
    if product.is_available:
        product.is_available = False
        product.save()
    else:
        product.is_available = True
        product.save()
    
    return redirect('productList')

def deleteCategory(request , pk):
    category = Category.objects.get(id=pk)
    category.delete()
    return redirect('categoryList')

def searchOrder(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            orders = Order.objects.order_by('-order_number').filter(Q(first_name__icontains=keyword) | Q(order_number__icontains=keyword))
            order_count = orders.count()
    context ={
       'orders' :orders,
       'order_count' : order_count,
       'keyword' : keyword,
    }
    return render(request,'manager/dashboard.html',context)

def searchProduct(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-product_name').filter(Q(product_name__icontains=keyword) | Q(description__icontains=keyword))
            product_count = products.count()
    context ={
       'products' :products,
       'product_count' : product_count,
       'keyword' : keyword,
    }
    return render(request,'manager/product_list.html',context)

def searchCategory(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            categories = Category.objects.order_by('-category_name').filter(Q(category_name__icontains=keyword) | Q(description__icontains=keyword))
            categories_count = categories.count()
    context ={
       'categories' :categories,
       'categories_count' : categories_count,
       'keyword' : keyword,
    }
    return render(request,'manager/category_list.html',context)


def orderDetail(request , order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity
    statuses = Order.STATUS 
    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
        'statuses' : statuses,
    }
    return render(request, 'manager/order_detail.html', context)


def updateOrderStatus(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        order = Order.objects.get(order_number=order_id)
        order.status = new_status
        order.save()
        messages.success(request, 'Status updated successfully!')
        return redirect('orderDetail',order_id)
    
def addUser(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listUser')
    else:
        form = UserForm()
    return render(request,'manager/add_user.html',{'form': form})

def userList(request):
    users = Account.objects.filter(user_type='User').order_by('-date_joined')
    paginator = Paginator(users, 10)
    page = request.GET.get('page')
    paged_users = paginator.get_page(page)
    context = {
     'products': paged_users,
     }
    return render(request,'manager/user_list.html',context)

def userEdit(request,pk):

    user = Account.objects.get(id=pk)
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST , instance=user)
        if form.is_valid():
            form.save()
            return redirect('listUser')

    context = {

    'product': user,

    'form': form,

    }
    return render(request,'manager/user_edit.html',context)

def deleteUser(request, pk):
    user = Account.objects.get(id=pk)
    if user.is_active:
        user.is_active = False
        user.save()
    else:
        user.is_active = True
        user.save()
    
    return redirect('listUser')
        
def wallet(request):
    wallet = Wallet.objects.all()

    context = {
        "wallets" : wallet
    }
    return render(request,'manager/wallet.html',context)

def walletTransactions(request):
    wallet_transactions = WalletTransaction.objects.all()
    context = {
        "wallet_transactions" : wallet_transactions
    }
    return render(request,'manager/wallet_transactions.html',context)

def addCoupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listCoupon')
    else:
        form = CouponForm()
    return render(request,'manager/add_coupon.html',{'form': form})

def couponList(request):
    coupons = Coupon.objects.all().order_by('valid_from')
    paginator = Paginator(coupons, 10)
    page = request.GET.get('page')
    paged_coupons = paginator.get_page(page)
    context = {
     'coupons': paged_coupons,
     }
    return render(request,'manager/coupon_list.html',context)

def deleteCoupon(request, pk):
    coupon = Coupon.objects.get(id=pk)
    if coupon.active:
        coupon.active = False
        coupon.save()
    else:
        coupon.active = True
        coupon.save()
    
    return redirect('listCoupon')

def couponEdit(request,pk):
    coupon = Coupon.objects.get(id=pk)
    form = CouponForm(instance=coupon)

    if request.method == 'POST':
        form = CouponForm(request.POST , instance=coupon)
        if form.is_valid():
            form.save()
            return redirect('listCoupon')

    context = {

    'product': coupon,

    'form': form,

    }
    return render(request,'manager/coupon_edit.html',context)

def reviewList(request):
    reviews = ReviewRating.objects.all()
    context = {

    'reviews': reviews

    }
    return render(request,'manager/review_list.html',context)

def editreviewList(request,pk):
    print("Heyy")
    review = ReviewRating.objects.get(id=pk)
    print(review.status)
    if review.status:
        review.status = False
        review.save()
    else:
        review.status = True
        review.save()
    return redirect('reviewList')

def searchWalletTransactions(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            walletTransactions = WalletTransaction.objects.order_by('-timestamp').filter(Q(user__username__icontains=keyword) | Q(transaction_type__icontains=keyword))
    context = {
        "wallet_transactions" : walletTransactions
    }
    return render(request,'manager/wallet_transactions.html',context)

def searchCoupons(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            coupons = Coupon.objects.order_by('-valid_from').filter(Q(code__icontains=keyword))
            paginator = Paginator(coupons, 10)
            page = request.GET.get('page')
            paged_coupons = paginator.get_page(page)
    context ={
       'coupons' :paged_coupons,
    }
    return render(request,'manager/coupon_list.html',context)