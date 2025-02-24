from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal

class Product(models.Model):
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_level = models.PositiveIntegerField(default=0)
    reorder_point = models.PositiveIntegerField(default=10)
    location = models.CharField(max_length=50)
    quickbooks_id = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.sku})"

class InventoryTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('receive', 'Receive'),
        ('ship', 'Ship'),
        ('adjust', 'Adjust'),
        ('transfer', 'Transfer'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    reference = models.CharField(max_length=50)  # Order number, adjustment ID, etc.
    notes = models.TextField(blank=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.product.name} - {self.quantity}"

    def save(self, *args, **kwargs):
        if self.transaction_type in ['receive', 'adjust']:
            self.product.stock_level += self.quantity
        elif self.transaction_type == 'ship':
            self.product.stock_level -= self.quantity
        self.product.save()
        super().save(*args, **kwargs)

class PickingList(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    order = models.OneToOneField('sales.Order', on_delete=models.CASCADE, related_name='picking_list')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Picking List for Order {self.order.order_number}"

class PickingListItem(models.Model):
    picking_list = models.ForeignKey(PickingList, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    picked_quantity = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=50)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.product.name} x {self.quantity} (Picking List: {self.picking_list.id})"

class Warehouse(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
