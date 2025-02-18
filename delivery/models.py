from django.db import models
from django.contrib.auth.models import User

class Delivery(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('rescheduled', 'Rescheduled'),
    ]
    
    order = models.OneToOneField('sales.Order', on_delete=models.CASCADE, related_name='delivery')
    route = models.ForeignKey('management.Route', on_delete=models.SET_NULL, null=True)
    stop = models.ForeignKey('management.CustomerStop', on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    delivered_at = models.DateTimeField(null=True, blank=True)
    proof_of_delivery = models.ImageField(upload_to='proof_of_delivery/', null=True, blank=True)
    signature = models.ImageField(upload_to='signatures/', null=True, blank=True)
    notes = models.TextField(blank=True)
    qb_txn_id = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Delivery for Order {self.order.order_number}"

    class Meta:
        ordering = ['route', 'stop']
        verbose_name_plural = "Deliveries"

class DeliveryException(models.Model):
    EXCEPTION_TYPES = [
        ('missing_items', 'Missing Items'),
        ('damaged_items', 'Damaged Items'),
        ('rejected_items', 'Rejected Items'),
        ('rejected_order', 'Rejected Order'),
        ('customer_unavailable', 'Customer Unavailable'),
        ('wrong_address', 'Wrong Address'),
        ('other', 'Other'),
    ]
    
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='exceptions')
    exception_type = models.CharField(max_length=20, choices=EXCEPTION_TYPES)
    description = models.TextField()
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    reported_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_exception_type_display()} - {self.delivery}"

class VanLoadingRecord(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('verified', 'Verified'),
    ]

    route = models.ForeignKey('management.Route', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    loaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='van_loading')
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='van_verifications')
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Van Loading for Route {self.route.name} - {self.route.date}"
