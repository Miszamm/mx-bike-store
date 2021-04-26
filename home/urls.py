from django.contrib import admin
from django.urls import path
from .views import (
    HomeView,
    ItemDetailView,
    checkout,
    OrderSummaryView,
    add_to_cart,
    remove_from_cart,
)

app_name = 'home'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('checkout/', checkout, name='checkout'),
    path('order_summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart')
]
