from django import forms
from django.core.validators import EmailValidator
from accounts.models import Account
from orders.models import Coupon
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_date

from store.models import Product,Category

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code','discount','valid_from','valid_to','active']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter code'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter discount'}),
            'valid_from': forms.DateInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter from date'},
                format='%Y-%m-%d',  # Adjust the format as needed
            ),
            'valid_to': forms.DateInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter to date'},
                format='%Y-%m-%d',  # Adjust the format as needed
            ),
        }

class UserForm(forms.ModelForm):
    email = forms.EmailField(
        validators=[EmailValidator(message='Enter a valid email address.')],
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email'})
    )

    class Meta:
        model = Account
        fields = ['email', 'username', 'first_name', 'last_name', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter firstname'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter describtion'}),
        }

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['is_active'].initial = True
        self.fields['is_active'].widget.attrs['disabled'] = 'disabled'

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')

        cleaned_data['is_active'] = True
        
        if not username or not email or not first_name or not last_name:
            raise forms.ValidationError('All fields are required.')



class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name','slug','description','price','images','stock','is_available', 'category']
        widgets = {
            'product_name' : forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Enter product name'}),
            'slug' : forms.TextInput(attrs={'class':'form-control' , 'placeholder': 'Enter url'}),
            'description' : forms.Textarea(attrs={'class':'form-control' , 'placeholder': 'Enter description'}),
            'price': forms.NumberInput(attrs={'class': 'form-control' ,  'placeholder': 'Enter price'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control' ,  'placeholder': 'Enter stock'}),
            'is_available': forms.CheckboxInput(),
            'category': forms.Select(attrs={'class': 'form-control'}), 
        }
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name','slug','description','cat_image']
        widgets = {
            'category_name' : forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Enter category name'}),
            'slug' : forms.TextInput(attrs={'class':'form-control' , 'placeholder': 'Enter url'}),
            'description' : forms.TextInput(attrs={'class':'form-control' , 'placeholder': 'Enter describtion'}),
        }


    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['category'].widget = forms.Select()  # Override the widget to use a Select dropdown