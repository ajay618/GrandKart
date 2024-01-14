from accounts.forms import WalletForm
from orders.models import Wallet, WalletTransaction
from store.models import Product
from django.shortcuts import render

def home(request):
    products = Product.objects.all().filter(is_available=True).order_by('created_date')
    context = {
        'products': products,
    }
    return render(request , 'home.html',context)

def my_wallet(request):
    user = request.user  # Get the current logged-in user
    wallet = Wallet.objects.get(user=user)
    if request.method == 'POST':
        form = WalletForm(request.POST)
        if form.is_valid():
            adding_balance = form.cleaned_data['balance']
            current_balance = wallet.balance  # Retrieve current balance
            wallet.balance = current_balance + adding_balance  # Update the balance
            wallet.save()  # Save the updated wallet
            WalletTransaction.objects.create(user=user, amount=adding_balance, transaction_type='credit')
            balance = wallet.balance  # Get the updated balance
            form = WalletForm()
            order_number = request.session.get('order_number')
            wallet_transactions = WalletTransaction.objects.filter(user=user).order_by('-timestamp')

            context = {
                "balance": balance,
                "form": form,
                "order_number":order_number,
                "wallet_transactions":wallet_transactions, 
            
            }
            return render(request, 'accounts/my_wallet.html', context)
    else:
        form = WalletForm()  # Provide the existing wallet instance to the form
        balance = wallet.balance
        order_number = request.session.get('order_number')
        wallet_transactions = WalletTransaction.objects.filter(user=user).order_by('-timestamp')
        context = {
            "balance": balance,
            "form": form,
            "order_number":order_number,
            "wallet_transactions":wallet_transactions,
            
        }
        return render(request, 'accounts/my_wallet.html', context)