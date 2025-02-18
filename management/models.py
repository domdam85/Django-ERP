from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class Route(models.Model):
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    name = models.CharField(max_length=100)
    day = models.CharField(max_length=20)  # Day of week
    territory = models.CharField(max_length=100)
    sales_rep = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sales_routes')
    delivery_driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='delivery_routes')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    notes = models.TextField(blank=True)
    qb_list_id = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.name} - {self.day}"

    class Meta:
        ordering = ['day', 'name']

class CustomerStop(models.Model):
    customer = models.ForeignKey('sales.Customer', on_delete=models.CASCADE)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='stops')
    sequence = models.PositiveIntegerField()
    
    class Meta:
        ordering = ['route', 'sequence']
        unique_together = ['route', 'sequence']

class PerformanceMetric(models.Model):
    METRIC_TYPES = [
        ('sales', 'Sales Performance'),
        ('delivery', 'Delivery Performance'),
        ('warehouse', 'Warehouse Performance'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='performance_metrics')
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES)
    date = models.DateField()
    value = models.DecimalField(max_digits=10, decimal_places=2)
    target = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_metric_type_display()} - {self.date}"

    class Meta:
        ordering = ['-date']
        unique_together = ['user', 'metric_type', 'date']

class Report(models.Model):
    REPORT_TYPES = [
        ('daily', 'Daily Report'),
        ('weekly', 'Weekly Report'),
        ('monthly', 'Monthly Report'),
        ('custom', 'Custom Report'),
    ]
    
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_report_type_display()})"

    class Meta:
        ordering = ['-created_at']

class Goal(models.Model):
    GOAL_TYPES = [
        ('sales', 'Sales Target'),
        ('delivery', 'Delivery Target'),
        ('inventory', 'Inventory Target'),
    ]
    
    title = models.CharField(max_length=200)
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPES)
    target_value = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    progress = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.assigned_to.get_full_name()}"

    class Meta:
        ordering = ['-end_date']

class Notification(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.user.get_full_name()}"

    class Meta:
        ordering = ['-created_at']

class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateTimeField()
    priority = models.CharField(max_length=10, choices=Notification.PRIORITY_CHOICES, default='medium')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.assigned_to.get_full_name()}"

    class Meta:
        ordering = ['-due_date']
