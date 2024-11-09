from rest_framework.permissions import BasePermission

class HasPurchasedProduct(BasePermission):
    def has_permission(self, request, view):
        product = view.get_object()  # Assuming `view.get_object()` gets the product object
        return product.order_set.filter(user=request.user, is_paid=True).exists()