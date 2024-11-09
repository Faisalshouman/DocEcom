from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Product , Cart , CartItem ,Order , OrderItem
from .serializers import ProductSerializer , CartItemSerializer , OrderSerializer , OrderItemSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.throttling import UserRateThrottle
from rest_framework.permissions import IsAuthenticated
from .permissions import HasPurchasedProduct


@method_decorator(cache_page(60 * 15), name='dispatch')  # Cache for 15 minutes
class ProductListCreateView(APIView):
    throttle_classes = [UserRateThrottle]
    def get(self, request):
        # Caching, pagination, and throttling applied here automatically
        products = Product.objects.all()
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductDetailView(APIView):
    throttle_classes = [UserRateThrottle]
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND

    def get(self, request, pk):
        product = self.get_object(pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, pk):
        product = self.get_object(pk)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            serializer = ProductSerializer(product, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        product = self.get_object(pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class CartView(APIView):
    throttle_classes = [UserRateThrottle]
    permission_classes = [IsAuthenticated]
    def post(self, request, pk):
        try:
            # Retrieve the user's cart; create one if it doesn't exist
            user_cart, created = Cart.objects.get_or_create(user=request.user)

            # Get the product the user wants to add to the cart
            product = Product.objects.get(pk=pk)

            # Check if the product is already in the cart
            cart_item, item_created = CartItem.objects.get_or_create(
                cart=user_cart,
                product=product,
                defaults={'quantity': 1}  # Default quantity when adding the product to the cart
            )

            # If the product is already in the cart, increase the quantity
            if not item_created:
                cart_item.quantity += 1
                cart_item.save()

            # Serialize the cart item
            serializer = CartItemSerializer(cart_item)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Product.DoesNotExist:
            # Return an error if the product is not found
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        
class OrderCreateView(APIView):
    throttle_classes = [UserRateThrottle]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Get the user's cart
            user_cart = Cart.objects.get(user=request.user)
            # Get all items in the user's cart
            cart_items = CartItem.objects.filter(cart=user_cart)

            # Create a new order
            user_order = Order.objects.create(user=request.user, total_price=0)
            total_price = 0

            # Loop over each cart item and create an order item
            for cart_item in cart_items:
                order_item = OrderItem.objects.create(
                    order=user_order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price * cart_item.quantity
                )
                total_price += order_item.price  # Accumulate total order price
            
            # Update the total price of the order
            user_order.total_price = total_price
            user_order.save()

            # Clear the cart
            cart_items.delete()
            user_cart.delete()

            # Serialize the order items and respond
            serializer = OrderItemSerializer(OrderItem.objects.filter(order=user_order), many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Cart.DoesNotExist:
            return Response({"detail": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        
class ProductDownloadView(APIView):
    permission_classes = [IsAuthenticated ,HasPurchasedProduct]

    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        order = Order.objects.filter(user=request.user, is_paid=True).first()
        if order and product in order.items.all():
            return Response({'pdf_url': product.pdf_file.url})
        return Response({'detail': 'Access denied or product not purchased'}, status=status.HTTP_403_FORBIDDEN)