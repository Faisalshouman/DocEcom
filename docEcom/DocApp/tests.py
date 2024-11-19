from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Product, Order, OrderItem
from .permissions import HasPurchasedProduct
import json
from unittest.mock import patch


class ECommerceTestCase(APITestCase):
    def setUp(self):
        # Create users
        self.admin_user = User.objects.create_superuser(username="admin", password="admin123")
        self.customer_user = User.objects.create_user(username="customer", password="password123")

        # Create products
        self.product1 = Product.objects.create(name="Product 1", description="Test product 1", price=10.0)
        self.product2 = Product.objects.create(name="Product 2", description="Test product 2", price=20.0)

        # Create an order for the customer
        self.order = Order.objects.create(user=self.customer_user, is_paid=True)
        self.order_item = OrderItem.objects.create(order=self.order, product=self.product1, quantity=1)

        # API client
        self.client = APIClient()rom django.test import TestCase
        
        
class PermissionTests(ECommerceTestCase):
    def test_customer_has_purchased_product(self):
        # Simulate a request with customer user
        request = self.client.get(f"/products/{self.product1.id}/download/")
        request.user = self.customer_user
        permission = HasPurchasedProduct()

        # Test permission
        view = None  # Replace with a mock view if required
        self.assertTrue(permission.has_permission(request, view))

    def test_customer_has_not_purchased_product(self):
        # Simulate a request with customer user
        request = self.client.get(f"/products/{self.product2.id}/download/")
        request.user = self.customer_user
        permission = HasPurchasedProduct()

        # Test permission
        view = None  # Replace with a mock view if required
        self.assertFalse(permission.has_permission(request, view))

class ProductListCreateViewTests(ECommerceTestCase):
    def test_get_products(self):
        response = self.client.get("/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Assuming pagination

    def test_create_product_as_admin(self):
        self.client.login(username="admin", password="admin123")
        response = self.client.post("/products/", {"name": "Product 3", "description": "Test product 3", "price": 30.0})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_product_as_non_admin(self):
        self.client.login(username="customer", password="password123")
        response = self.client.post("/products/", {"name": "Product 3", "description": "Test product 3", "price": 30.0})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class ProductDownloadViewTests(ECommerceTestCase):
    def test_download_purchased_product(self):
        self.client.login(username="customer", password="password123")
        response = self.client.get(f"/products/{self.product1.id}/download/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("pdf_url", response.data)

    def test_download_unpurchased_product(self):
        self.client.login(username="customer", password="password123")
        response = self.client.get(f"/products/{self.product2.id}/download/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_download_product_not_found(self):
        self.client.login(username="customer", password="password123")
        response = self.client.get("/products/999/download/")  # Non-existent product
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)



class PayPalWebhookTests(ECommerceTestCase):
    @patch("paypalrestsdk.WebhookEvent.verify")
    def test_successful_webhook(self, mock_verify):
        mock_verify.return_value = True

        payload = json.dumps({
            "event_type": "PAYMENT.SALE.COMPLETED",
            "resource": {"invoice_id": str(self.order.id)}
        })
        response = self.client.post("/paypal/webhook/", payload, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the order is marked as paid
        self.order.refresh_from_db()
        self.assertTrue(self.order.is_paid)

    @patch("paypalrestsdk.WebhookEvent.verify")
    def test_invalid_signature(self, mock_verify):
        mock_verify.return_value = False

        payload = json.dumps({
            "event_type": "PAYMENT.SALE.COMPLETED",
            "resource": {"invoice_id": str(self.order.id)}
        })
        response = self.client.post("/paypal/webhook/", payload, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_not_found(self):
        payload = json.dumps({
            "event_type": "PAYMENT.SALE.COMPLETED",
            "resource": {"invoice_id": "9999"}  # Non-existent order ID
        })
        response = self.client.post("/paypal/webhook/", payload, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)