from django.urls import path
from . import views

urlpatterns = [
     path('place_order/', views.place_order, name='place_order'),
    #path('payments/', views.payments, name='payments'),
     path('cash_on_delivery' , views.cashondelivery , name='cash_on_delivery'),
     path('order_complete/', views.order_complete, name='order_complete'),
]