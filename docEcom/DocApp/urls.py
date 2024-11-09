# DocApp/urls.py
from django.urls import path
from .views import (
    ProductListCreateView,
    ProductDetailView,
    CartView,
    CartAddItemView,
    CartRemoveItemView,
    OrderCreateView,
    OrderListView,
    OrderDetailView,
    ProductDownloadView,
)
from .payment import paypal_webhook, PayPalPaymentView

urlpatterns = [
    # Product-related URLs
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),

    # Cart-related URLs
    path('cart/', CartView.as_view(), name='cart-view'),
    path('cart/add/<int:pk>/', CartAddItemView.as_view(), name='cart-add-item'),
    path('cart/remove/<int:pk>/', CartRemoveItemView.as_view(), name='cart-remove-item'),

    # Order-related URLs
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/create/', OrderCreateView.as_view(), name='order-create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),

    # Product download for purchased items
    path('products/<int:pk>/download/', ProductDownloadView.as_view(), name='product-download'),

    # PayPal webhook for payment confirmation
    path('payment/', PayPalPaymentView.as_view(), name='paypal-payment'),
    path('webhook/paypal/', paypal_webhook, name='paypal-webhook'),

]


