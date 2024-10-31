from rest_framework import serializers
from .models import Product, Cart, CartItem, Order, OrderItem

# Serializer for Product model
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'pdf_file', 'image']

# Serializer for CartItem model
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()  # Nested serializer to show product details in the cart

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']

# Serializer for Cart model
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)  # Nested serializer to show all items in the cart

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items']

# Serializer for OrderItem model
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()  # Nested serializer to show product details in the order

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']

# Serializer for Order model
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)  # Nested serializer to show all items in the order

    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'total_price', 'is_paid', 'items']
