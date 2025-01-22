from django.contrib import admin 
from django.urls import path 
from .views import Index, store, Signup, Login, logout, Checkout, OrderView, Cart, products_by_category, product_detail

urlpatterns = [ 
	path('', Index.as_view(), name='homepage'), 
	path('store', store, name='store'), 
	path('category/<slug:category_slug>', products_by_category, name='products_by_category'),
	path('product/<slug:product_slug>', product_detail, name='product_detail'),
	path('signup', Signup.as_view(), name='signup'), 
	path('login', Login.as_view(), name='login'), 
	path('logout', logout, name='logout'), 
	path('cart', Cart.as_view(), name='cart'),
	path('check-out', Checkout.as_view(), name='checkout'), 
	path('orders', OrderView.as_view(), name='orders'), 

] 
