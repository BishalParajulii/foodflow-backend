# Payment Implementation Plan

## Overview
Implement the Payments app to handle payment processing for orders, including:
- Payment models (Payment, Transaction, Refund)
- Integration with Orders app
- Basic payment processing flow
- Admin interface
- Tests

## Files to Create/Modify

### 1. Payment Models (`backend/apps/payments/models.py`)
```python
from django.db import models
from django.conf import settings
from apps.common.models import BaseModel
from apps.orders.models import Order

class PaymentMethod(models.TextChoices):
    CASH_ON_DELIVERY = 'cod', 'Cash on Delivery'
    ESewA = 'esewa', 'eSewa'
    KHALTI = 'khalti', 'Khalti'
    STRIPE = 'stripe', 'Stripe'
    BANK_TRANSFER = 'bank_transfer', 'Bank Transfer'

class PaymentStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    PROCESSING = 'processing', 'Processing'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'
    REFUNDED = 'refunded', 'Refunded'
    PARTIALLY_REFUNDED = 'partially_refunded', 'Partially Refunded'

class Payment(BaseModel):
    """Payment record for an order."""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']

class Transaction(BaseModel):
    """Individual transaction attempts."""
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices)
    gateway_response = models.JSONField(default=dict, blank=True)
    gateway_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']

class Refund(BaseModel):
    """Refund record."""
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('failed', 'Failed')
    ], default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    refunded_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
```

### 2. Payment Serializers (`backend/apps/payments/serializers.py`)
```python
from rest_framework import serializers
from .models import Payment, Transaction, Refund, PaymentMethod, PaymentStatus

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'amount', 'method', 'status', 'transaction_id', 'paid_at', 'created_at']
        read_only_fields = ['id', 'created_at']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'payment', 'amount', 'status', 'gateway_transaction_id', 'created_at']

class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = ['id', 'payment', 'amount', 'reason', 'status', 'transaction_id', 'refunded_at']
```

### 3. Payment Views (`backend/apps/payments/views.py`)
```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Payment, Transaction, Refund
from .serializers import PaymentSerializer, TransactionSerializer, RefundSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        payment = self.get_object()
        # Basic payment processing logic (to be integrated with actual gateways)
        if payment.status == PaymentStatus.PENDING:
            payment.status = PaymentStatus.PROCESSING
            payment.save()
            
            # Create transaction record
            Transaction.objects.create(
                payment=payment,
                amount=payment.amount,
                status=PaymentStatus.PROCESSING,
                gateway_response={'test': 'true'}
            )
            
            # Simulate successful payment
            payment.status = PaymentStatus.COMPLETED
            payment.transaction_id = f"test_{payment.id}"
            payment.paid_at = timezone.now()
            payment.gateway_response = {'status': 'success', 'test': True}
            payment.save()
            
            # Update transaction
            payment.transactions.last().status = PaymentStatus.COMPLETED
            payment.transactions.last().save()
            
            return Response({'status': 'payment processed'})
        return Response({'error': 'Invalid payment status'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        payment = self.get_object()
        if payment.status != PaymentStatus.COMPLETED:
            return Response({'error': 'Can only refund completed payments'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        amount = request.data.get('amount', payment.amount)
        if amount > payment.amount:
            return Response({'error': 'Refund amount exceeds payment amount'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        refund = Refund.objects.create(
            payment=payment,
            amount=amount,
            reason=request.data.get('reason', ''),
            status='processed',
            transaction_id=f"refund_{payment.id}",
            refunded_at=timezone.now()
        )
        
        if amount == payment.amount:
            payment.status = PaymentStatus.REFUNDED
        else:
            payment.status = PaymentStatus.PARTIALLY_REFUNDED
        payment.save()
        
        return Response(RefundSerializer(refund).data)
```

### 4. Payment URLs (`backend/apps/payments/urls.py`)
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('api/', include(router.urls)),
]
```

### 5. Payment Admin (`backend/apps/payments/admin.py`)
```python
from django.contrib import admin
from .models import Payment, Transaction, Refund

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'amount', 'method', 'status', 'paid_at']
    list_filter = ['method', 'status', 'created_at']
    search_fields = ['order__id', 'transaction_id']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'payment', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    readonly_fields = ['created_at']

@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['id', 'payment', 'amount', 'status', 'refunded_at']
    list_filter = ['status', 'created_at']
    readonly_fields = ['created_at']
```

### 6. Payment Apps Config (`backend/apps/payments/apps.py`)
```python
from django.apps import AppConfig

class PaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.payments'
    verbose_name = 'Payments'
```

### 7. Update Orders Model to Add Payment Relationship
In `backend/apps/orders/models.py`, add to Order model:
```python
# Add this import
from apps.payments.models import Payment

# Add this property to Order model
@property
def payment(self):
    """Get related payment if exists."""
    return getattr(self, '_payment', None)
```

### 8. Update Main URLs (`backend/config/urls.py`)
```python
# Add payments URLs
path('api/payments/', include('apps.payments.urls')),
```

### 9. Create Migrations
```bash
python backend/manage.py makemigrations payments
python backend/manage.py migrate
```

### 10. Payment Tests (`backend/apps/payments/tests.py`)
```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.orders.models import Order
from apps.restaurants.models import Restaurant, Branch
from apps.menu.models import MenuItem, ModifierGroup, ModifierOption
from apps.carts.models import Cart
from apps.payments.models import Payment, Transaction, Refund

User = get_user_model()

class PaymentModelTest(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create restaurant
        self.restaurant = Restaurant.objects.create(
            owner=self.user,
            name='Test Restaurant',
            address='Test Address',
            phone='1234567890'
        )
        
        # Create branch
        self.branch = Branch.objects.create(
            restaurant=self.restaurant,
            name='Main Branch',
            address='Test Address'
        )
        
        # Create menu item
        self.menu_item = MenuItem.objects.create(
            restaurant=self.restaurant,
            name='Test Item',
            price=10.00
        )
        
        # Create cart
        self.cart = Cart.objects.create(
            user=self.user,
            restaurant=self.restaurant,
            branch=self.branch
        )
        
        # Create order
        self.order = Order.objects.create(
            user=self.user,
            restaurant=self.restaurant,
            branch=self.branch,
            status='pending',
            subtotal=10.00,
            delivery_fee=5.00,
            total=15.00,
            delivery_address='Test Address',
            phone='1234567890'
        )

    def test_payment_creation(self):
        payment = Payment.objects.create(
            order=self.order,
            amount=15.00,
            method='cod',
            status='pending'
        )
        self.assertEqual(payment.order, self.order)
        self.assertEqual(payment.amount, 15.00)
        self.assertEqual(payment.method, 'cod')
        self.assertEqual(payment.status, 'pending')

    def test_payment_processing(self):
        payment = Payment.objects.create(
            order=self.order,
            amount=15.00,
            method='cod',
            status='pending'
        )
        # Simulate processing
        payment.status = 'processing'
        payment.save()
        self.assertEqual(payment.status, 'processing')
        
        # Simulate completion
        payment.status = 'completed'
        payment.paid_at = timezone.now()
        payment.save()
        self.assertEqual(payment.status, 'completed')
```

## Dependencies
- Orders app must be fully implemented
- Django REST Framework
- Basic payment gateway integrations (to be added later)

## Estimated Effort
- Models: 2 hours
- Serializers: 1 hour
- Views: 2 hours
- URLs/Admin: 1 hour
- Tests: 2 hours
- Integration: 1 hour
- Total: ~9 hours

## Next Steps After Payments
1. Delivery app implementation
2. Notifications app implementation  
3. Analytics app implementation
4. Promotions app implementation