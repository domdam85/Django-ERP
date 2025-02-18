from django.contrib import admin
from .quickbooks.models import QuickBooksSettings, Customer

# Register your models here.

@admin.register(QuickBooksSettings)
class QuickBooksSettingsAdmin(admin.ModelAdmin):
    list_display = ('conductor_end_user_id', 'sync_enabled', 'last_sync_time')
    readonly_fields = ('last_sync_time',)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'company_name', 'contact_name', 'sync_status', 'last_sync_time')
    list_filter = ('sync_status', 'is_active')
    search_fields = ('name', 'company_name', 'contact_name', 'email')
    readonly_fields = ('qb_list_id', 'qb_time_modified', 'last_sync_time', 'sync_status', 'sync_error')
    fieldsets = (
        (None, {
            'fields': ('name', 'company_name', 'contact_name', 'phone', 'email', 'is_active')
        }),
        ('Addresses', {
            'fields': ('billing_address', 'shipping_address')
        }),
        ('QuickBooks Sync', {
            'fields': ('qb_list_id', 'qb_time_modified', 'last_sync_time', 'sync_status', 'sync_error'),
            'classes': ('collapse',)
        })
    )
