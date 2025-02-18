from conductor import Conductor
from django.conf import settings
from .models import QuickBooksSettings

def get_conductor_client():
    """Get configured Conductor client using settings from database"""
    try:
        qb_settings = QuickBooksSettings.objects.first()
        if not qb_settings:
            raise ValueError("QuickBooks settings not configured")
            
        return Conductor(
            api_key=qb_settings.conductor_api_key
        ), qb_settings.conductor_end_user_id
    except QuickBooksSettings.DoesNotExist:
        raise ValueError("QuickBooks settings not configured")
