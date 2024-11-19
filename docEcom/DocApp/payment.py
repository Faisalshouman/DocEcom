import paypalrestsdk
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Order
import json
from django.views.decorators.csrf import csrf_exempt

# Set up PayPal SDK
paypalrestsdk.configure({
    'mode': settings.PAYPAL_MODE,
    'client_id': settings.PAYPAL_CLIENT_ID,
    'client_secret': settings.PAYPAL_CLIENT_SECRET
})

class PayPalPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        order = Order.objects.get(pk=pk, user=request.user, is_paid=False)
        payment = paypalrestsdk.Payment({
            'intent': 'sale',
            'payer': {
                'payment_method': 'paypal'
            },
            'redirect_urls': {
                'return_url': 'http://localhost:8000/payment/execute/',
                'cancel_url': 'http://localhost:8000/payment/cancel/'
            },
            'transactions': [{
                'amount': {
                    'total': str(order.total_price),
                    'currency': 'USD'
                },
                'description': f'Payment for order {order.id}'
            }]
        })

        if payment.create():
            for link in payment.links:
                if link.rel == 'approval_url':
                    approval_url = link.href
                    return Response({'approval_url': approval_url})

        return Response({"detail": "Payment creation failed."}, status=status.HTTP_400_BAD_REQUEST)

@@csrf_exempt
def paypal_webhook(request):
    webhook_id = settings.PAYPAL_WEBHOOK_ID
    transmission_id = request.headers.get('PayPal-Transmission-Id')
    timestamp = request.headers.get('PayPal-Transmission-Time')
    signature = request.headers.get('PayPal-Transmission-Sig')
    cert_url = request.headers.get('PayPal-Cert-Url')
    auth_algo = request.headers.get('PayPal-Auth-Algo')

    body = request.body.decode('utf-8')
    event = json.loads(body)
    
    if not paypalrestsdk.WebhookEvent.verify(
        transmission_id=transmission_id,
        timestamp=timestamp,
        webhook_id=webhook_id,
        event_body=body,
        cert_url=cert_url,
        actual_sig=signature,
        auth_algo=auth_algo
    ):
        return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)

    event_type = event.get('event_type')
    if event_type == 'PAYMENT.SALE.COMPLETED':
        sale = event['resource']
        order_id = sale['invoice_id']  # Assuming invoice_id was set to your order ID
        try:
            order = Order.objects.get(id=order_id)
            order.is_paid = True
            order.save()
            return Response({'status': 'Order updated successfully'}, status=200)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=404)

    return Response({'status': 'Event received'}, status=status.HTTP_200_OK)