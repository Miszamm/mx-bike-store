from django.urls import path
from .views import (
    ItemDetailView,
    ShopView,
    AdminProductList,
    AdminProductCreateView,
    AdminProductUpdateView,
    AdminProductDeleteView,
)
# app_name = 'home'

urlpatterns = [
    path('shop', ShopView.as_view(), name='shop'),
    path('admin_product_list', AdminProductList.as_view(), name='admin_product_list'),
    path('admin_product/add/', AdminProductCreateView.as_view(), name='admin_product-add'),
    path('admin_product/<int:pk>/', AdminProductUpdateView.as_view(), name='admin_product-update'),
    path('admin_product/<int:pk>/delete/', AdminProductDeleteView.as_view(), name='admin_product-delete'),
    path('product/<slug>', ItemDetailView.as_view(), name='product'),
]
