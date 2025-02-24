from django.db import models
from django.contrib.auth.models import User

class Route(models.Model):
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    name = models.CharField(max_length=100)
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='routes')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.date}"

    class Meta:
        ordering = ['-date', 'name']

class Delivery(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('rescheduled', 'Rescheduled'),
    ]
    
    order = models.OneToOneField('sales.Order', on_delete=models.CASCADE, related_name='delivery')
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, related_name='deliveries')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sequence = models.PositiveIntegerField(help_text="Delivery sequence in the route")
    scheduled_time = models.TimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    proof_of_delivery = models.ImageField(upload_to='proof_of_delivery/', null=True, blank=True)
    signature = models.ImageField(upload_to='signatures/', null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Delivery for Order {self.order.order_number}"

    class Meta:
        ordering = ['route', 'sequence']
        verbose_name_plural = "Deliveries"

class DeliveryException(models.Model):
    EXCEPTION_TYPES = [
        ('address_not_found', 'Address Not Found'),
        ('customer_unavailable', 'Customer Unavailable'),
        ('vehicle_breakdown', 'Vehicle Breakdown'),
        ('weather', 'Weather Conditions'),
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

class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ('van', 'Van'),
        ('truck', 'Truck'),
        ('car', 'Car'),
    ]
    
    name = models.CharField(max_length=100)
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPES)
    license_plate = models.CharField(max_length=20)
    capacity = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.license_plate})"
