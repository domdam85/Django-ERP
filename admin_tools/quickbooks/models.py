from django.db import models
from django.utils import timezone

class QuickBooksModelMixin(models.Model):
    qb_list_id = models.CharField(max_length=100, unique=True, null=True)
    qb_time_modified = models.DateTimeField(null=True)
    last_sync_time = models.DateTimeField(null=True)
    sync_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('synced', 'Synced'),
        ('error', 'Error')
    ], default='pending')
    sync_error = models.TextField(null=True, blank=True)
    
    class Meta:
        abstract = True

class QuickBooksSettings(models.Model):
    """Settings for QuickBooks integration"""
    conductor_api_key = models.CharField(max_length=255)
    conductor_end_user_id = models.CharField(max_length=255)
    last_sync_time = models.DateTimeField(null=True)
    sync_enabled = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'QuickBooks Settings'
        verbose_name_plural = 'QuickBooks Settings'

    def __str__(self):
        return f"QuickBooks Settings (End User: {self.conductor_end_user_id})"

    def save(self, *args, **kwargs):
        if not self.pk and QuickBooksSettings.objects.exists():
            # Ensure only one settings instance exists
            return QuickBooksSettings.objects.first()
        return super(QuickBooksSettings, self).save(*args, **kwargs)

class SyncSession(models.Model):
    """Records a QuickBooks synchronization session"""
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ]
    
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    total_objects = models.IntegerField(default=0)
    synced_objects = models.IntegerField(default=0)
    failed_objects = models.IntegerField(default=0)
    progress_percentage = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-start_time']
        get_latest_by = 'start_time'
    
    def __str__(self):
        return f"Sync {self.start_time.strftime('%Y-%m-%d %H:%M:%S')} ({self.status})"
    
    def duration(self):
        """Calculate session duration"""
        if self.end_time:
            return self.end_time - self.start_time
        return timezone.now() - self.start_time

    def mark_completed(self):
        """Mark the session as completed"""
        self.status = 'completed'
        self.end_time = timezone.now()
        self.save()
    
    def mark_failed(self):
        """Mark the session as failed"""
        self.status = 'failed'
        self.end_time = timezone.now()
        self.save()

class SyncError(models.Model):
    """Records an error that occurred during synchronization"""
    session = models.ForeignKey(SyncSession, on_delete=models.CASCADE, related_name='errors')
    timestamp = models.DateTimeField(auto_now_add=True)
    object_type = models.CharField(max_length=50)
    object_id = models.CharField(max_length=50, null=True, blank=True)
    error_message = models.TextField()
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Error in {self.object_type}: {self.error_message[:50]}"

class Customer(QuickBooksModelMixin):
    """QuickBooks customer record"""
    SYNC_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('synced', 'Synced'),
        ('error', 'Error')
    ]
    
    name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    contact_name = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    billing_address = models.TextField(null=True, blank=True)
    shipping_address = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        ordering = ['name']

    def __str__(self):
        return self.name
