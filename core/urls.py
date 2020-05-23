from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from .views import (home_view, HomeView, ItemDetailedView,add_to_cart
					,remove_from_cart,Payment, OrderSummary,remove_single_item_from_cart,CheckoutView,AddCouponView)
app_name = 'core'

urlpatterns = [
    path('',HomeView.as_view(),name='home'),
    path('product/<slug>/',ItemDetailedView.as_view(), name='product'),
    path('add-to-cart/<slug>/',add_to_cart,name='add-to-cart'),
    path('remove-from-cart/<slug>/',remove_from_cart,name='remove-from-cart'),
    path('order-summary/',OrderSummary.as_view(),name='order-summary'),
    path('remove-single-item-from-cart/<slug>/',remove_single_item_from_cart,name='remove-single-item-from-cart'),
    path('checkout/',CheckoutView.as_view(),name='checkout'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('pay/', Payment.as_view(), name='payment')
]
