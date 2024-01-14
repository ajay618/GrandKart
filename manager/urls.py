from django.urls import path
from . import views


urlpatterns = [
    path('',views.admindashboard, name='admindashboard'),
    path('addProduct/',views.addProduct , name='addProduct'),
    path('addCategory/',views.addCategory , name='addCategory'),
    path('productList/',views.productList , name='productList'),
    path('categoryList/',views.categoryList , name='categoryList'),
    path('editProduct/<int:pk>/', views.editProduct, name='editProduct'),
    path('editCategory/<int:pk>/', views.editCategory, name='editCategory'),
    path('deleteProduct/<int:pk>/', views.deleteProduct, name='deleteProduct'),
    path('deleteCategory/<int:pk>/', views.deleteCategory, name='deleteCategory'),
    path('search_order/', views.searchOrder, name='searchOrder'),
    path('search_product/', views.searchProduct, name='searchProduct'),
    path('search_category/', views.searchCategory, name='searchCategory'),
    path('search_couponList', views.searchCoupons, name='searchCoupons'),
    path('search_wallettransactions/', views.searchWalletTransactions, name='searchWalletTransactions'),
    path('order_detail/<int:order_id>',views.orderDetail, name="orderDetail"),
    path('update_order_status/',views.updateOrderStatus,name="updateOrderStatus"),
    path('add_user/',views.addUser,name="addUser"),
    path('userList/',views.userList,name="listUser"),
    path('add_coupon/',views.addCoupon,name="addCoupon"),
    path('couponList/',views.couponList,name="listCoupon"),
    path('deleteCoupon/<int:pk>/', views.deleteCoupon, name='deleteCoupon'),
    path('couponEdit/<int:pk>/',views.couponEdit,name="editCoupon"),
    path('userEdit/<int:pk>/',views.userEdit,name="editUser"),
    path('deleteUser/<int:pk>/', views.deleteUser, name='deleteUser'),
    path('wallet/',views.wallet,name='wallet'),
    path('wallet_transactions/',views.walletTransactions,name="walletTransactions"),
    path('review_list/',views.reviewList,name="reviewList"),
    path('edit_review_list/<int:pk>/',views.editreviewList,name="editreviewList"),

]