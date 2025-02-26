# QuickBooks Sync Implementation Plan

## Directory Structure
```
admin_tools/
└── sync/
    ├── __init__.py
    ├── manager.py           # Core sync management
    ├── base.py             # Base sync class
    ├── registry.py         # Registry for sync objects
    ├── exceptions.py       # Custom exceptions
    └── objects/            # Individual sync implementations
        ├── __init__.py     # Registers all sync objects
        ├── customer.py     # Independent data
        ├── vendor.py       # Independent data
        ├── item.py         # Independent data
        ├── order.py        # Depends on customers & items
        ├── invoice.py      # Depends on customers & items
        └── adjustment.py   # Depends on items
```

## Implementation Steps

### Phase 1: Core Infrastructure (2-3 days)

1. **Base Models** (4-6 hours)
```python
# admin_tools/models.py
from django.db import models

class SyncSession(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    selected_objects = models.JSONField(default=list)  # List of object types to sync
    error_count = models.IntegerField(default=0)

    # Dynamic progress fields will be created for each registered sync object

    current_object = models.CharField(max_length=50, blank=True)
    current_record_id = models.CharField(max_length=255, blank=True) # Store QBD ID
    total_records = models.IntegerField(default=0)
    processed_records = models.IntegerField(default=0)

    def progress_percentage(self):
        if self.total_records == 0:
            return 0
        return int((self.processed_records / self.total_records) * 100)

class SyncError(models.Model):
    session = models.ForeignKey(SyncSession, on_delete=models.CASCADE)
    object_type = models.CharField(max_length=50)
    object_id = models.CharField(max_length=100, null=True, blank=True) # Store QBD ID
    error_message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
```

2. **Base Classes** (4-6 hours)
```python
# admin_tools/sync/base.py
from abc import ABC, abstractmethod

class BaseSyncObject(ABC):
    name = ''  # e.g. "customer"
    display_name = ''  # e.g. "Customers"
    qb_list_method = ''  # e.g. "customers.list"
    depends_on = []  # e.g. ["customer", "item"] for orders

    def __init__(self, conductor_client, session_id):
        self.client = conductor_client
        self.session = SyncSession.objects.get(id=session_id)

    @abstractmethod
    def get_local_model(self):
        """Return Django model to sync with"""
        pass

    @abstractmethod
    def map_qb_to_local(self, qb_object):
        """Map QB object to local model fields"""
        pass

    def get_total_records(self):
        """Get total records to sync for progress tracking"""
        # Default implementation (override if needed)
        method = getattr(self.client.qbd, self.qb_list_method)
        return method().total_count

    def update_progress(self, record_id):
        """Update sync progress"""
        self.session.current_record_id = record_id
        self.session.processed_records += 1
        self.session.save()

    @abstractmethod
    def sync(self):
        """Main sync logic"""
        self.session.current_object = self.name
        total = self.get_total_records()
        self.session.total_records = total
        self.session.save()
```

3. **Registry** (2-3 hours)
```python
# admin_tools/sync/registry.py
from typing import Dict, Type
from .base import BaseSyncObject

class SyncRegistry:
    def __init__(self):
        self._registry: Dict[str, Type[BaseSyncObject]] = {}

    def register(self, sync_class: Type[BaseSyncObject]):
        if not sync_class.name:
            raise ValueError("Sync class must define a name")
        self._registry[sync_class.name] = sync_class

    def get_sync_class(self, name: str) -> Type[BaseSyncObject]:
        return self._registry.get(name)

    def get_all_objects(self):
        """Return all registered objects"""
        return self._registry.items()

    def get_independent_objects(self):
        """Get objects with no dependencies"""
        return [obj for name, obj in self._registry.items()
                if not obj.depends_on]

    def get_dependent_objects(self):
        """Get objects with dependencies"""
        return [obj for name, obj in self._registry.items()
                if obj.depends_on]

# Global instance
sync_registry = SyncRegistry()
```

4. **Sync Manager** (1 day)
```python
# admin_tools/sync/manager.py
from typing import List
from django.utils import timezone
from conductor import Conductor
from .registry import sync_registry
from .exceptions import SyncError
from ..models import SyncSession, SyncError

class SyncManager:
    def __init__(self, api_key: str):
        self.client = Conductor(api_key=api_key)

    def _create_session(self, sync_type: str, object_types: List[str]) -> SyncSession:
        """Create a new sync session"""
        return SyncSession.objects.create(
            status='pending',
            selected_objects=object_types
        )

    def start_sync(self, object_types: List[str] = None):
        """Start sync with optional object type filtering"""
        session = self._create_session('full', object_types) # Always full for now

        try:
            session.status = 'in_progress'
            session.save()

            # Sync independent objects first
            independent = sync_registry.get_independent_objects()
            for sync_class in independent:
                if not object_types or sync_class.name in object_types:
                    sync_obj = sync_class(self.client, session.id)
                    sync_obj.sync()

            # Then sync dependent objects
            dependent = sync_registry.get_dependent_objects()
            for sync_class in dependent:
                if not object_types or sync_class.name in object_types:
                    sync_obj = sync_class(self.client, session.id)
                    sync_obj.sync()

            session.status = 'completed'
            session.completed_at = timezone.now()
            session.save()

        except Exception as e:
            session.status = 'failed'
            session.save()
            # Log the exception
            SyncError.objects.create(session=session, error_message=str(e))
            raise

    def get_sync_status(self, session_id):
        """Get detailed sync status"""
        session = SyncSession.objects.get(id=session_id)
        return {
            'status': session.status,
            'started_at': session.started_at,
            'completed_at': session.completed_at,
            'current_object': session.current_object,
            'current_record_id': session.current_record_id,
            'total_records': session.total_records,
            'processed_records': session.processed_records,
            'progress_percentage': session.progress_percentage(),
            'error_count': session.error_count,
            'selected_objects': session.selected_objects
        }
```

5. **Exceptions**
```python
# admin_tools/sync/exceptions.py
class SyncError(Exception):
    """Base class for sync exceptions"""
    pass
```

### Phase 2: UI Implementation (1-2 days)

1. **Templates** (1 day)
```html
<!-- admin_tools/templates/admin_tools/sync/dashboard.html -->
{% extends "admin_tools/base.html" %}

{% block content %}
<div class="container">
    <!-- Object Selection -->
    <div class="card mb-4">
        <div class="card-header">
            <h5>QuickBooks Sync</h5>
        </div>
        <div class="card-body">
            <form hx-post="{% url 'admin_tools:start_sync' %}"
                  hx-swap="none">
                {% csrf_token %}
                <div class="mb-3">
                    <label>Select Objects to Sync</label>
                    {% for name, obj in sync_objects %}
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox"
                               name="objects" value="{{ obj.name }}"
                               id="check_{{ obj.name }}">
                        <label class="form-check-label"
                               for="check_{{ obj.name }}">
                            {{ obj.display_name }}
                        </label>
                    </div>
                    {% endfor %}
                </div>
                <button class="btn btn-primary" type="submit">
                    Start Sync
                </button>
            </form>
        </div>
    </div>

    <!-- Progress Section -->
    <div class="card mb-4"
         hx-get="{% url 'admin_tools:sync_progress' %}"
         hx-trigger="load every 2s">
        <div class="card-header">
            <h5>Sync Progress</h5>
        </div>
        <div class="card-body">
            {% if current_sync %}
                <p>Status: {{ current_sync.status }}</p>
                <p>Current Object: {{ current_sync.current_object }}</p>
                <p>Current Record: {{ current_sync.current_record_id }}</p>
                <div class="progress">
                    <div class="progress-bar" role="progressbar"
                         style="width: {{ current_sync.progress_percentage }}%;"
                         aria-valuenow="{{ current_sync.progress_percentage }}"
                         aria-valuemin="0" aria-valuemax="100">
                        {{ current_sync.progress_percentage }}%
                    </div>
                </div>
                <p>Processed: {{ current_sync.processed_records }} / {{ current_sync.total_records }}</p>
                <p>Errors: {{ current_sync.error_count }}</p>
            {% else %}
                <p>No active sync session.</p>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}
```

```html
<!-- admin_tools/templates/admin_tools/sync/includes/progress.html -->
{% if current_sync %}
    <p>Status: {{ current_sync.status }}</p>
    <p>Current Object: {{ current_sync.current_object }}</p>
    <p>Current Record: {{ current_sync.current_record_id }}</p>
    <div class="progress">
        <div class="progress-bar" role="progressbar"
                style="width: {{ current_sync.progress_percentage }}%;"
                aria-valuenow="{{ current_sync.progress_percentage }}"
                aria-valuemin="0" aria-valuemax="100">
            {{ current_sync.progress_percentage }}%
        </div>
    </div>
    <p>Processed: {{ current_sync.processed_records }} / {{ current_sync.total_records }}</p>
    <p>Errors: {{ current_sync.error_count }}</p>
{% else %}
    <p>No active sync session.</p>
{% endif %}
```

2. **Views** (1 day)
```python
# admin_tools/views.py
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from .sync.manager import SyncManager
from .sync.registry import sync_registry
from django.conf import settings
from django.http import JsonResponse

@staff_member_required
def sync_dashboard(request):
    """Main sync interface"""
    context = {
        'sync_objects': sync_registry.get_all_objects()
    }
    return render(request, 'admin_tools/sync/dashboard.html', context)

@staff_member_required
def start_sync(request):
    """Starts a new sync session"""
    if request.method == 'POST':
        object_types = request.POST.getlist('objects')
        manager = SyncManager(api_key=settings.CONDUCTOR_API_KEY)
        manager.start_sync(object_types)
        return redirect('admin_tools:sync_dashboard')  # Redirect to dashboard
    return redirect('admin_tools:sync_dashboard')

@staff_member_required
def sync_progress(request):
    """Returns sync progress as JSON for HTMX updates"""
    # Get the most recent sync session
    session = SyncSession.objects.order_by('-started_at').first()
    if session:
        manager = SyncManager(api_key=settings.CONDUCTOR_API_KEY)
        status = manager.get_sync_status(session.id)
        return render(request, 'admin_tools/sync/includes/progress.html', {'current_sync': status})
    else:
        return render(request, 'admin_tools/sync/includes/progress.html', {'current_sync': None})
```

3. **URLs**
```python
# admin_tools/urls.py
from django.urls import path
from . import views

app_name = 'admin_tools'

urlpatterns = [
    # ... other URLs ...
    path('sync/', views.sync_dashboard, name='sync_dashboard'),
    path('sync/start/', views.start_sync, name='start_sync'),
    path('sync/progress/', views.sync_progress, name='sync_progress'),
]
```

4. **Add to base.html**
```html
<head>
    <!-- ... other head elements ... -->
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
</head>
```

5. **Add to left_nav.html**
```html
<li class="left-nav-item">
    <a href="{% url 'admin_tools:sync_dashboard' %}" class="left-nav-link {% if request.resolver_match.url_name == 'sync_dashboard' %}active{% endif %}">
        <i class="fas fa-sync-alt left-nav-icon"></i>
        <span class="left-nav-text">QuickBooks Sync</span>
    </a>
</li>
```

### Phase 3: Implement Sync Objects (Ongoing)

1. **Customer Sync**
```python
# admin_tools/sync/objects/customer.py
from ..base import BaseSyncObject
from sales.models import Customer

class CustomerSync(BaseSyncObject):
    name = "customer"
    display_name = "Customers"
    qb_list_method = "customers.list"

    def get_local_model(self):
        return Customer

    def map_qb_to_local(self, qb_object):
        return {
            'name': qb_object['name'],
            'quickbooks_id': qb_object['id'],
            'email': qb_object.get('email', ''),
            'phone': qb_object.get('phone', ''),
            'address': qb_object.get('billing_address', {}).get('address1', '')
        }

    def sync(self):
        super().sync() # Update session with total records
        
        method = getattr(self.client.qbd, self.qb_list_method)
        for qb_object in method(conductor_end_user_id=settings.CONDUCTOR_END_USER_ID):
            try:
                mapped_data = self.map_qb_to_local(qb_object)
                obj, created = self.get_local_model().objects.update_or_create(
                    quickbooks_id=qb_object['id'],
                    defaults=mapped_data
                )
                self.update_progress(qb_object['id'])
            except Exception as e:
                SyncError.objects.create(session=self.session, object_type=self.name, object_id=qb_object.get('id'), error_message=str(e))
                self.session.error_count += 1
                self.session.save()
```

2. **Item Sync** (Similar structure to CustomerSync)
3. **Vendor Sync** (Similar structure to CustomerSync)
4. **Order Sync** (Depends on CustomerSync and ItemSync)
5. **Invoice Sync** (Depends on CustomerSync and ItemSync)
6. **Adjustment Sync** (Depends on ItemSync)

### Phase 4: Testing & Refinement (Ongoing)

1. **Unit Tests**
2. **Integration Tests**
3. **Manual Testing**

### Register Sync Objects
```python
# admin_tools/sync/objects/__init__.py
from ..registry import sync_registry
from .customer import CustomerSync
# from .item import ItemSync
# from .vendor import VendorSync
# from .order import OrderSync
# from .invoice import InvoiceSync
# from .adjustment import AdjustmentSync

sync_registry.register(CustomerSync)
# sync_registry.register(ItemSync)
# sync_registry.register(VendorSync)
# sync_registry.register(OrderSync)
# sync_registry.register(InvoiceSync)
# sync_registry.register(AdjustmentSync)
```

## Detailed Steps for Each Object Type (Retain from original plan)

### 1. Customers

*   **Script:** `admin_tools/sync/objects/customer.py`
*   **Direction:** Bidirectional
*   **Steps:**
    1.  **Fetch from QuickBooks:**
        *   Use `conductor.qbd.customers.list()` with appropriate parameters (e.g., `updated_at__gt` to fetch only modified customers since the last sync).
        *   Handle pagination using the auto-pagination features of the Conductor API.
    2.  **Fetch from WMS:**
        *   Query the `Customer` model (in `sales/models.py`).
    3.  **Compare and Update:**
        *   Iterate through the QuickBooks customers.
        *   For each customer:
            *   If a matching customer exists in the WMS (based on `quickbooks_id`):
                *   Compare attributes.
                *   If changes are detected:
                    *   Apply conflict resolution rules (QBD is authoritative, except for contact details).
                    *   Update the WMS customer record.
            *   If no matching customer exists:
                *   Create a new WMS customer record.
    4.  **(Two-way Sync) Fetch from WMS:**
        *   Query the `Customer` model for records modified since the last sync (using a `last_synced_to_qb` timestamp or similar).
    5.  **(Two-way Sync) Push to QuickBooks:**
        *   For each modified/new WMS customer:
            *   If the customer exists in QuickBooks (check `quickbooks_id`):
                *   Use `conductor.qbd.customers.update()` to update the QuickBooks record.
            *   If the customer is new:
                *   Use `conductor.qbd.customers.create()` to create the QuickBooks record.
                *   Store the returned `id` in the WMS customer's `quickbooks_id` field.
    6.  **Error Handling:**
        *   Catch any exceptions during the API calls or database operations.
        *   Log errors and associate them with the `SyncSession`.
        *   Implement retry logic for transient errors (e.g., network issues).
    7.  **Progress Reporting:**
        *   Update the `SyncSession` object with the number of customers processed, synced, and failed.

### 2. Items (All Types)

*   **Script(s):** `admin_tools/sync/objects/item.py` (or separate scripts for each item type)
*   **Direction:** Bidirectional
*   **Steps:** (Similar to Customers, but with more complexity due to multiple item types)
    1.  **Fetch from QuickBooks:**
        *   Use `conductor.qbd.inventory_items.list()`, `conductor.qbd.non_inventory_items.list()`, etc., for each relevant item type.
        *   Use appropriate parameters to filter for modified items.
    2.  **Fetch from WMS:**
        *   Query the appropriate item models (e.g., `InventoryItem`, `NonInventoryItem`).
    3.  **Compare and Update:**
        *   Iterate through the QuickBooks items.
        *   For each item:
            *   If a matching item exists in the WMS (based on `quickbooks_id` or a combination of attributes):
                *   Compare attributes.
                *   If changes are detected:
                    *   Apply conflict resolution rules (latest timestamp wins).
                    *   Update the WMS item record.
            *   If no matching item exists:
                *   Create a new WMS item record.
    4.  **(Two-way Sync) Fetch from WMS:**
        *   Query the item models for records modified since the last sync.
    5.  **(Two-way Sync) Push to QuickBooks:**
        *   For each modified/new WMS item:
            *   If the item exists in QuickBooks:
                *   Use the appropriate `update()` method (e.g., `conductor.qbd.inventory_items.update()`).
            *   If the item is new:
                *   Use the appropriate `create()` method.
                *   Store the returned `id` in the WMS item record.
    6.  **Error Handling:** (Same as Customers)
    7.  **Progress Reporting:**
        *   Update the `SyncSession` object with the number of items processed, synced, and failed.

### 3. Sales Orders

*   **Script:** `admin_tools/sync/objects/order.py`
*   **Direction:** Bidirectional
*   **Steps:** (Similar to Customers/Items)
    1.  **Fetch from QuickBooks:**
        *   Use `conductor.qbd.sales_orders.list()` with appropriate filtering.
    2.  **Fetch from WMS:**
        *   Query the `Order` model (in `sales/models.py`).
    3.  **Compare and Update:**
        *   Iterate through QuickBooks sales orders.
        *   Match with WMS orders (likely using `quickbooks_id`).
        *   Create or update WMS orders.
        *   **Important:** Handle order lines (items) carefully. This might involve a separate loop to sync order items.
    4.  **(Two-way Sync) Fetch from WMS:**
        *   Query for modified/new WMS orders.
    5.  **(Two-way Sync) Push to QuickBooks:**
        *   Use `create()` or `update()` methods.
        *   **Important:** Ensure proper mapping of order lines to QuickBooks item references.
    6.  **Error Handling:** (Same as Customers)
    7.  **Progress Reporting:**
        *   Update the `SyncSession` object with the number of sales orders processed, synced, and failed.

### 4. Purchase Orders

*   **Script:** `admin_tools/sync/objects/purchase_order.py`
*   **Direction:** Bidirectional
*   **Steps:** (Similar to Sales Orders)
    1.  **Fetch from QuickBooks:** `conductor.qbd.purchase_orders.list()`
    2.  **Fetch from WMS:** Query a `PurchaseOrder` model (which needs to be created/updated).
    3.  **Compare and Update:** Match, create, or update WMS purchase orders and their line items.
    4.  **(Two-way Sync) Fetch from WMS:** Query for modified/new WMS purchase orders.
    5.  **(Two-way Sync) Push to QuickBooks:** Use `create()` or `update()`.
    6.  **Error Handling:** (Same as Customers)
    7.  **Progress Reporting:**
        *   Update the `SyncSession` object with the number of purchase orders processed, synced, and failed.

### 5. Inventory Adjustments

*   **Script:** `admin_tools/sync/objects/adjustment.py`
*   **Direction:** Bidirectional
*   **Steps:**
    1.  **Fetch from QuickBooks:** `conductor.qbd.inventory_adjustments.list()` (Note: This previously timed out, so alternative approaches might be needed.  Consider fetching inventory levels for all items and calculating adjustments based on differences.)
    2.  **Fetch from WMS:** Query an `InventoryAdjustment` model (which needs to be created).
    3.  **Compare and Update:**
        *   This will likely involve calculating the *net* change in inventory, as per the conflict resolution rule.
        *   Create or update WMS inventory adjustment records.
    4.  **(Two-way Sync) Fetch from WMS:** Query for new/modified WMS inventory adjustments.
    5.  **(Two-way Sync) Push to QuickBooks:** Use `create()` or `update()`.
    6.  **Error Handling:** (Same as Customers)
    7.  **Progress Reporting:**
        *   Update the `SyncSession` object with the number of inventory adjustments processed, synced, and failed.

### 6. Invoices

*   **Script:** `admin_tools/sync/objects/invoice.py`
*   **Direction:** One-Way (QBD → WMS)
*   **Steps:**
    1.  **Fetch from QuickBooks:** `conductor.qbd.invoices.list()`
    2.  **Fetch from WMS:** Query an `Invoice` model (which needs to be created - potentially in the `sales` app).
    3.  **Compare and Update:**
        *   Create or update WMS invoice records.  *No updates should be pushed back to QuickBooks.*
    4.  **Error Handling:** (Same as Customers)
    5.  **Progress Reporting:**
        *   Update the `SyncSession` object with the number of invoices processed, synced, and failed.

### 7. Vendors
* **Script:** `admin_tools/sync/objects/vendor.py`
* **Direction:** Bidirectional
* **Steps:** (Similar to Customers)

## UI Integration (Retain from original plan)

The existing `admin_tools/templates/admin_tools/quickbooks/sync_dashboard.html` template provides the UI for initiating and monitoring syncs. The `SyncManager` will provide methods to:

*   **`start_sync(objects_to_sync)`:** Starts a sync session for the specified objects.
*   **`cancel_sync()`:** Cancels any currently running sync session. (Not implemented yet)
*   **`get_sync_status()`:** Returns the status of the current (or most recent) sync session, including:
    *   `status`: ('running', 'completed', 'failed', 'cancelled')
    *   `started_at`: Datetime when the sync started.
    *   `completed_at`: Datetime when the sync ended (or None if still running).
    *   `selected_objects`: List of objects selected for sync
    *   `current_object`: Object type currently being synced
    *   `current_record_id`: QBD ID of current record
    *   `total_records`: Total number of records to sync for current object
    *   `processed_records`: Number of records processed for current object
    *   `progress_percentage`: Overall progress percentage.
    *   `error_count`: Total errors
*   **`get_sync_history()`:** Returns a history of sync sessions. (Not implemented yet)

The `sync_progress` view (in `admin_tools/views.py`) will be updated to use the `SyncManager.get_sync_status()` method to fetch the necessary information. This view will be an HTMX endpoint, periodically polled by the `sync_dashboard.html` template to update the UI elements (progress bar, error messages, etc.).

**Specific UI Elements:**

*   **Start Button:** Button to initiate the synchronization.
*   **Object Selection:** Checkboxes to select which objects to sync.
*   **Progress Bar:** A visual indicator of the overall sync progress.
*   **Status Indicator:** Text displaying the current sync status (e.g., "Running," "Completed," "Failed").
*   **Current Object/Record:** Display current object and record being processed.
*   **Error Log:** A section displaying any errors encountered during the synchronization. This should include the object type, object ID (if available), and a description of the error.
* **Last Sync Time:** Display the date and time of the last successful synchronization. (Not implemented yet)

**Sync History Interface (`sync_history.html`)** (Not implemented yet)

The `sync_history.html` template will display a table of past synchronization sessions, using `django-tables2`.  The `SyncManager.get_sync_history()` method will provide the data for this table. The table will include:

*   Start Time
*   End Time
*   Status (Completed, Failed, Cancelled)
*   Objects Synced
*   Duration
*   Link to view detailed error logs (if any) for that session.

## Bootstrap Theme

**All UI elements, including the sync dashboard and sync history, will be styled using Bootstrap 5 to ensure a consistent look and feel with the rest of the application.** The existing templates already demonstrate the use of Bootstrap classes.

## Conductor API Integration Details (Retain from original plan)

This section provides details on using the Conductor API client for synchronization.

### 1. Installation

The Conductor Python library is installed via pip:

```bash
pip install conductor-py
```

### 2. Client Initialization

The Conductor API client can be initialized in two ways: synchronous and asynchronous. The `SyncManager` will use the synchronous client, and individual sync scripts can choose the appropriate client type based on their needs.

**Synchronous Client:**

```python
import os
from conductor import Conductor

conductor = Conductor(
    api_key=os.environ.get("CONDUCTOR_SECRET_KEY"),  # Recommended: Use environment variable
)

# Alternatively, provide the API key directly (less secure):
# conductor = Conductor(api_key="YOUR_SECRET_KEY")
```

**Asynchronous Client:**

```python
import os
import asyncio
from conductor import AsyncConductor

conductor = AsyncConductor(
    api_key=os.environ.get("CONDUCTOR_SECRET_KEY"),
)

# Usage with asyncio:
# async def main():
#     # ... API calls using await ...
# asyncio.run(main())
```

**Recommendation:** Use `python-dotenv` to store the `CONDUCTOR_SECRET_KEY` in a `.env` file, keeping it out of your source code.  The `CONDUCTOR_END_USER_ID` should be stored in the Django settings.

### 3. Basic API Usage

The Conductor API provides methods for creating, reading, updating, and deleting (CRUD) QuickBooks objects.  The general pattern is:

```python
# List objects (replace 'customers' with the appropriate resource)
page = conductor.qbd.customers.list(conductor_end_user_id=settings.CONDUCTOR_END_USER_ID)
for customer in page:  # Auto-pagination
    print(customer.id, customer.name)

# Retrieve a specific object
customer = conductor.qbd.customers.retrieve(
    id="CUSTOMER_ID",
    conductor_end_user_id=settings.CONDUCTOR_END_USER_ID
)
print(customer.name, customer.billing_address)

# Create a new object
new_customer = conductor.qbd.customers.create(
    conductor_end_user_id=settings.CONDUCTOR_END_USER_ID,
    name="New Customer",
    company_name="New Company",
    # ... other required fields ...
)

# Update an existing object
updated_customer = conductor.qbd.customers.update(
    id="CUSTOMER_ID",
    conductor_end_user_id=settings.CONDUCTOR_END_USER_ID,
    name="Updated Customer Name",
)

# Delete an object (if supported)
# response = conductor.qbd.customers.delete(
#     id="CUSTOMER_ID",
#     conductor_end_user_id=settings.CONDUCTOR_END_USER_ID
# )
```

**Important:** Always include the `conductor_end_user_id` parameter in your API calls.

### 4. Pagination

The `list()` methods in the Conductor API are paginated. The library provides auto-pagination, so you can iterate through all results without manually handling pagination:

```python
all_customers = []
for customer in conductor.qbd.customers.list(conductor_end_user_id=settings.CONDUCTOR_END_USER_ID):
    all_customers.append(customer)
```

For more granular control, you can use the `has_next_page()`, `next_page_info()`, and `get_next_page()` methods.

### 5. Error Handling

The Conductor API client raises exceptions for various error conditions:

*   **`conductor.APIConnectionError`:**  Unable to connect to the API (e.g., network issues).
*   **`conductor.APIStatusError`:**  The API returned a non-success status code (4xx or 5xx).  This exception includes `status_code` and `response` properties.
*   **`conductor.RateLimitError`:**  A 429 status code was received (rate limit exceeded).
*   **`conductor.APITimeoutError`:** The request timed out.

You should wrap your API calls in `try...except` blocks to handle these errors gracefully:

```python
try:
    customers = conductor.qbd.customers.list(conductor_end_user_id=settings.CONDUCTOR_END_USER_ID)
    # ... process customers ...
except conductor.APIConnectionError as e:
    print(f"Connection error: {e}")
    # Handle connection error (e.g., retry later)
