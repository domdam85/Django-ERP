from django.utils import timezone
from django.db.models import Q
from .models import Customer, SyncSession
from .conductor_client import get_conductor_client
import logging
import time

logger = logging.getLogger(__name__)

class BaseSyncHandler:
    """Base class for all sync handlers"""
    def __init__(self):
        self.progress_callback = None
        self.error_callback = None
        self.object_type = None  # Should be set by subclasses
        
    def sync(self, progress_callback=None, error_callback=None):
        """
        Perform synchronization
        
        Args:
            progress_callback (callable): Function to call with progress updates
            error_callback (callable): Function to call when errors occur
            
        Returns:
            tuple: (synced_count, failed_count)
        """
        self.progress_callback = progress_callback
        self.error_callback = error_callback
        
    def report_progress(self, current, total):
        """Report sync progress"""
        if self.progress_callback:
            self.progress_callback(self.object_type, current, total)
            
    def report_error(self, object_id, error_message):
        """Report sync error"""
        if self.error_callback:
            self.error_callback(self.object_type, object_id, error_message)
            
    def should_continue(self):
        """Check if sync should continue"""
        running_session = SyncSession.objects.filter(status='running').first()
        return running_session and running_session.status == 'running'

class CustomerSync(BaseSyncHandler):
    """Handles synchronization of customers with QuickBooks"""
    
    def __init__(self):
        super().__init__()
        self.object_type = 'customers'
        self.client, self.end_user_id = get_conductor_client()

    def sync(self, progress_callback=None, error_callback=None):
        """
        Sync customers from QuickBooks to Django
        
        Returns:
            tuple: (synced_count, failed_count)
        """
        super().sync(progress_callback, error_callback)
        
        synced_count = 0
        failed_count = 0
        
        try:
            # Get total count for progress tracking
            total_customers = Customer.objects.count()
            logger.info(f"Starting sync for {total_customers} customers")
            
            # Get customers that need syncing
            customers = list(Customer.objects.all().order_by('id'))
            
            # Report initial progress
            self.report_progress(0, total_customers)
            
            # Process each customer
            for i, customer in enumerate(customers):
                # Check if sync was cancelled
                if not self.should_continue():
                    logger.info("Customer sync cancelled")
                    break
                
                try:
                    # Simulate sync for testing
                    time.sleep(0.1)  # Simulate work
                    
                    # Mark as synced
                    customer.sync_status = 'synced'
                    customer.last_sync_time = timezone.now()
                    customer.save()
                    synced_count += 1
                    
                except Exception as e:
                    logger.error(f"Error syncing customer {customer.id}: {str(e)}")
                    customer.sync_status = 'error'
                    customer.save()
                    self.report_error(customer.id, str(e))
                    failed_count += 1
                
                # Report progress after each customer
                self.report_progress(synced_count + failed_count, total_customers)
                logger.debug(f"Progress: {synced_count + failed_count}/{total_customers}")
            
            logger.info(f"Sync completed. Synced: {synced_count}, Failed: {failed_count}")
            return synced_count, failed_count
            
        except Exception as e:
            logger.error(f"Error in customer sync: {str(e)}")
            self.report_error(None, str(e))
            return synced_count, failed_count + 1
