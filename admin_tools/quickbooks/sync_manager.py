from django.utils import timezone
from .models import SyncSession, SyncError, Customer
from .sync import CustomerSync
import logging

logger = logging.getLogger(__name__)

class SyncManager:
    """Orchestrates the synchronization of multiple object types with QuickBooks"""
    
    def __init__(self):
        self.sync_handlers = {
            'customers': CustomerSync(),
            # More handlers will be added later
        }
        self.current_session = None
    
    def start_sync(self, object_types=None):
        """
        Start sync for specified object types or all if none specified
        
        Args:
            object_types (list): List of object types to sync. If None, syncs all types.
        
        Returns:
            SyncSession: The created sync session
        """
        try:
            # Cancel any existing running sessions
            SyncSession.objects.filter(status='running').update(
                status='cancelled',
                end_time=timezone.now()
            )
            
            # Create new sync session
            self.current_session = SyncSession.objects.create(
                status='running',
                total_objects=0  # Will be updated as we process each handler
            )
            
            # Determine which handlers to run
            handlers_to_run = {}
            if object_types:
                for obj_type in object_types:
                    if obj_type in self.sync_handlers:
                        handlers_to_run[obj_type] = self.sync_handlers[obj_type]
                    else:
                        logger.warning(f"Unknown object type: {obj_type}")
            else:
                handlers_to_run = self.sync_handlers
            
            # Calculate total objects
            total_objects = 0
            for obj_type, handler in handlers_to_run.items():
                if obj_type == 'customers':
                    total_objects += Customer.objects.count()
            
            self.current_session.total_objects = total_objects
            self.current_session.save()
            
            # Run each handler
            synced_total = 0
            failed_total = 0
            
            for obj_type, handler in handlers_to_run.items():
                try:
                    # Check if sync was cancelled
                    self.current_session.refresh_from_db()
                    if self.current_session.status == 'cancelled':
                        logger.info("Sync cancelled by user")
                        break
                        
                    logger.info(f"Starting sync for {obj_type}")
                    synced, failed = handler.sync(
                        progress_callback=self._progress_callback,
                        error_callback=self._error_callback
                    )
                    synced_total += synced
                    failed_total += failed
                    
                except Exception as e:
                    logger.error(f"Error syncing {obj_type}: {str(e)}")
                    self._error_callback(obj_type, None, str(e))
                    failed_total += 1
            
            # Update final status
            self.current_session.refresh_from_db()
            if self.current_session.status != 'cancelled':
                self.current_session.status = 'completed'
            self.current_session.end_time = timezone.now()
            self.current_session.synced_objects = synced_total
            self.current_session.failed_objects = failed_total
            self.current_session.save()
            
            return self.current_session
            
        except Exception as e:
            logger.error(f"Error in sync manager: {str(e)}")
            if self.current_session:
                self.current_session.status = 'failed'
                self.current_session.end_time = timezone.now()
                self.current_session.save()
                self._error_callback(None, None, str(e))
            raise
    
    def _progress_callback(self, object_type, current, total):
        """Update sync progress"""
        if self.current_session:
            try:
                self.current_session.refresh_from_db()
                if self.current_session.status == 'cancelled':
                    return
                    
                self.current_session.synced_objects = current
                self.current_session.progress_percentage = int((current / max(total, 1)) * 100)
                self.current_session.save()
                logger.debug(f"Progress updated: {current}/{total} ({self.current_session.progress_percentage}%)")
            except Exception as e:
                logger.error(f"Error updating progress: {str(e)}")
    
    def _error_callback(self, object_type, object_id, error_message):
        """Record sync error"""
        if self.current_session:
            try:
                SyncError.objects.create(
                    session=self.current_session,
                    object_type=object_type or 'unknown',
                    object_id=object_id,
                    error_message=error_message
                )
                logger.error(f"Sync error recorded: {error_message}")
            except Exception as e:
                logger.error(f"Error recording sync error: {str(e)}")
