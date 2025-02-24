# QuickBooks Synchronization Plan

This document outlines the plan for synchronizing data between the WMS system and QuickBooks Desktop using the Conductor API.

## Overall Architecture

*   **SyncManager:** A central class (`admin_tools/quickbooks/sync_manager.py`) responsible for managing the overall synchronization process. It will:
    *   Initiate and cancel sync sessions.
    *   Track sync progress and status (using the `SyncSession` model).
    *   Provide an interface for the UI to start/stop/monitor syncs.
    *   Delegate the actual synchronization of specific object types to individual sync scripts.

*   **Individual Sync Scripts:** Separate scripts for each object type (or group of related types) will handle the details of fetching, comparing, and updating data. These scripts will be located in `admin_tools/quickbooks/sync_scripts/`. Examples:
    *   `sync_customers.py`
    *   `sync_items.py` (This might be further divided into `sync_inventory_items.py`, `sync_non_inventory_items.py`, etc., if needed)
    *   `sync_sales_orders.py`
    *   `sync_purchase_orders.py`
    *   `sync_inventory_adjustments.py`

*   **Data Models:**
    *   Existing Django models will be used and updated as needed to align with the QuickBooks data structure.
    *   The temporary `Product` model will be replaced with specific item models (e.g., `InventoryItem`, `NonInventoryItem`, `ServiceItem`), inheriting from a common base class (`ItemBase`).

## Synchronization Direction and Conflict Resolution

The `Project_Summary.md` file specifies the synchronization direction and conflict resolution rules:

| Data Type               | Sync Direction        | Conflict Resolution                                                                 |
| ----------------------- | --------------------- | ----------------------------------------------------------------------------------- |
| Items (All Types)       | Bidirectional         | Latest timestamp wins.                                                              |
| Customers               | Bidirectional         | QBD is authoritative (unless only WMS changed contact details).                     |
| Vendors                 | Bidirectional         | (Not specified in Project_Summary - assume latest timestamp)                         |
| Sales Orders            | Bidirectional         | WMS is authoritative (since fulfillment happens there).                             |
| Invoices                | One-Way (QBD → WMS)   | N/A (one-way sync)                                                                  |
| Purchase Orders         | Bidirectional         | (Not specified in Project_Summary - assume latest timestamp, possibly WMS authority) |
| Inventory Adjustments   | Bidirectional         | Calculate the net change and update accordingly.                                     |

## Detailed Steps for Each Object Type

### 1. Customers

*   **Script:** `sync_customers.py`
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
            *   If a matching customer exists in the WMS (based on `id` or `qb_list_id`):
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
            *   If the customer exists in QuickBooks (check `qb_list_id`):
                *   Use `conductor.qbd.customers.update()` to update the QuickBooks record.
            *   If the customer is new:
                *   Use `conductor.qbd.customers.create()` to create the QuickBooks record.
                *   Store the returned `id` in the WMS customer's `qb_list_id` field.
    6.  **Error Handling:**
        *   Catch any exceptions during the API calls or database operations.
        *   Log errors and associate them with the `SyncSession`.
        *   Implement retry logic for transient errors (e.g., network issues).
    7.  **Progress Reporting:**
        *   Update the `SyncSession` object with the number of customers processed, synced, and failed.

### 2. Items (All Types)

*   **Script(s):** `sync_items.py` (or separate scripts for each item type)
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
            *   If a matching item exists in the WMS (based on `id` or a combination of attributes):
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

*   **Script:** `sync_sales_orders.py`
*   **Direction:** Bidirectional
*   **Steps:** (Similar to Customers/Items)
    1.  **Fetch from QuickBooks:**
        *   Use `conductor.qbd.sales_orders.list()` with appropriate filtering.
    2.  **Fetch from WMS:**
        *   Query the `Order` model (in `sales/models.py`).
    3.  **Compare and Update:**
        *   Iterate through QuickBooks sales orders.
        *   Match with WMS orders (likely using `qb_txn_id`).
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

*   **Script:** `sync_purchase_orders.py`
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

*   **Script:** `sync_inventory_adjustments.py`
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

*   **Script:** `sync_invoices.py`
*   **Direction:** One-Way (QBD → WMS)
*   **Steps:**
    1.  **Fetch from QuickBooks:** `conductor.qbd.invoices.list()`
    2.  **Fetch from WMS:** Query an `Invoice` model (which needs to be created - potentially in the `sales` app).
    3.  **Compare and Update:**
        *   Create or update WMS invoice records.  *No updates should be pushed back to QuickBooks.*
    4.  **Error Handling:** (Same as Customers)
    5.  **Progress Reporting:**
        *   Update the `SyncSession` object with the number of invoices processed, synced, and failed.

## UI Integration

The existing `admin_tools/templates/admin_tools/quickbooks/sync_dashboard.html` template provides the UI for initiating and monitoring syncs. The `SyncManager` will provide methods to:

*   **`start_sync(objects_to_sync)`:** Starts a sync session for the specified objects.
*   **`cancel_sync()`:** Cancels any currently running sync session.
*   **`get_sync_status()`:** Returns the status of the current (or most recent) sync session, including:
    *   `status`: ('running', 'completed', 'failed', 'cancelled')
    *   `start_time`: Datetime when the sync started.
    *   `end_time`: Datetime when the sync ended (or None if still running).
    *   `total_objects`: Total number of objects to be synced.
    *   `synced_objects`: Number of objects successfully synced.
    *   `failed_objects`: Number of objects that failed to sync.
    *   `progress_percentage`: Overall progress percentage.
    *   `object_progress`: A dictionary containing progress information for each object type being synced (e.g., `{'customers': {'total': 100, 'synced': 50, 'failed': 0}, 'items': ...}`).
    *   `errors`: A list of error messages (if any).
*   **`get_sync_history()`:** Returns a history of sync sessions.

The `sync_progress` view (in `admin_tools/quickbooks/views.py`) will be updated to use the `SyncManager.get_sync_status()` method to fetch the necessary information. This view will be an HTMX endpoint, periodically polled by the `sync_dashboard.html` template to update the UI elements (progress bar, error messages, etc.).

**Specific UI Elements:**

*   **Start/Cancel Buttons:** Buttons to initiate and cancel the synchronization.
*   **Progress Bar:** A visual indicator of the overall sync progress.
*   **Status Indicator:** Text displaying the current sync status (e.g., "Running," "Completed," "Failed").
*   **Object-Specific Progress:** A table or list showing the progress for each object type being synced (e.g., "Customers: 50/100," "Items: 20/200").
*   **Error Log:** A section displaying any errors encountered during the synchronization. This should include the object type, object ID (if available), and a description of the error.
* **Last Sync Time:** Display the date and time of the last successful synchronization.

**Sync History Interface (`sync_history.html`)**

The `sync_history.html` template will display a table of past synchronization sessions, using `django-tables2`.  The `SyncManager.get_sync_history()` method will provide the data for this table. The table will include:

*   Start Time
*   End Time
*   Status (Completed, Failed, Cancelled)
*   Total Objects
*   Synced Objects
*   Failed Objects
*   Duration
*   Link to view detailed error logs (if any) for that session.

## Bootstrap Theme

**All UI elements, including the sync dashboard and sync history, will be styled using Bootstrap 5 to ensure a consistent look and feel with the rest of the application.** The existing templates already demonstrate the use of Bootstrap classes.

## Conductor API Integration Details

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
except conductor.APIStatusError as e:
    print(f"API error: {e.status_code} - {e.response}")
    # Handle API error (e.g., log the error, skip the object)
except conductor.RateLimitError as e:
    print("Rate limit exceeded.  Backing off...")
    # Implement backoff strategy (e.g., wait and retry)
except conductor.APITimeoutError as e:
    print("Request timed out.")
    # Handle timeout (e.g., retry with a longer timeout)

```

The `SyncManager` and individual sync scripts should implement robust error handling, including logging errors to the `SyncSession` and potentially retrying failed operations.

### 6. Object Types and Fields

This section lists the QuickBooks object types that need to be synchronized, along with the relevant fields.  The field names are based on the `qb_api_inspection_20250222_095608.log` file and the Conductor API documentation.

**6.1 Customers**

*   **QuickBooks Resource:** `conductor.qbd.customers`
*   **Django Model:** `sales.models.Customer`
*   **Fields to Sync:**
    *   `id` (QuickBooks ID - primary key)
    *   `name`
    *   `company_name`
    *   `first_name`
    *   `last_name`
    *   `billing_address` (nested object - sync relevant fields like `line1`, `line2`, `city`, `state`, `postal_code`, `country`)
    *   `shipping_address` (nested object - same fields as billing_address)
    *   `phone`
    *   `email`
    *   `is_active`
    *   `created_at` (read-only from QuickBooks)
    *   `updated_at` (read-only from QuickBooks)
    *   `custom_fields` (if used - requires careful mapping)
    *   `balance` (read-only from QuickBooks)
    *   `total_balance` (read-only from QuickBooks)
    *   `currency`
    *   `customer_type` (nested object - sync `id` and `full_name`)
    *   `sales_representative` (nested object - sync `id` and `initial`)
    *   `terms` (nested object - sync `id` and `name`)
    *   `preferred_payment_method` (nested object - sync `id` and `name`)

**6.2 Items**

*   **QuickBooks Resources:**
    *   `conductor.qbd.inventory_items`
    *   `conductor.qbd.non_inventory_items`
    *   `conductor.qbd.service_items`
    *   `conductor.qbd.discount_items`
    *   `conductor.qbd.inventory_assembly_items`
    *   (Potentially others, depending on the specific item types used in QuickBooks)
*   **Django Models:**  Separate models for each item type (e.g., `InventoryItem`, `NonInventoryItem`, `ServiceItem`), inheriting from `warehouse.models.ItemBase`.
*   **Fields to Sync (InventoryItem - Example):**
    *   `id` (QuickBooks ID - primary key)
    *   `name`
    *   `full_name`
    *   `is_active`
    *   `description` (map to `sales_description` and/or `purchase_description` as appropriate)
    *   `sales_price`
    *   `purchase_cost`
    *   `quantity_on_hand` (one-way sync from QBD, as per Project_Summary)
    *   `quantity_on_order` (one-way sync from QBD)
    *   `quantity_on_sales_order` (one-way sync from QBD)
    *   `reorder_point`
    *   `asset_account` (nested object - sync `id` and `full_name`)
    *   `cogs_account` (nested object)
    *   `income_account` (nested object)
    *   `unit_of_measure_set` (nested object)
    *   `sales_tax_code` (nested object)
    *   `purchase_tax_code` (nested object)
    *   `preferred_vendor` (nested object)
    *   `custom_fields`

    *Other item types will have different fields, based on the `qb_api_inspection` log and the Conductor API documentation.*

**6.3 Sales Orders**

*   **QuickBooks Resource:** `conductor.qbd.sales_orders`
*   **Django Model:** `sales.models.Order`
*   **Fields to Sync:**
    *   `id` (QuickBooks ID - primary key)
    *   `customer` (nested object - use the synchronized `id` from the Customer sync)
    *   `transaction_date`
    *   `due_date`
    *   `billing_address` (nested object)
    *   `shipping_address` (nested object)
    *   `total_amount`
    *   `is_fully_invoiced`
    *   `is_manually_closed`
    *   `lines` (nested object - array of order lines)
        *   `item` (nested object - use the synchronized `id` from the Item sync)
        *   `quantity`
        *   `unit_price`
        *   `amount`
        *   `description`
    *   `memo`
    *   `sales_representative` (nested object)
    *   `sales_tax_code` (nested object)
    *   `sales_tax_item` (nested object)
    *   `sales_tax_percentage`
    *   `sales_tax_total`
    *   `terms` (nested object)
    *   `created_at`
    *   `updated_at`

**6.4 Purchase Orders**

*   **QuickBooks Resource:** `conductor.qbd.purchase_orders`
*   **Django Model:** `warehouse.models.PurchaseOrder` and `warehouse.models.PurchaseOrderLine`
*   **Fields to Sync:**
    *   `id`
    *   `vendor` (nested object)
    *   `transaction_date`
    *   `due_date`
    *   `expected_date`
    *   `total_amount`
    *   `is_fully_received`
    *   `is_manually_closed`
    *   `lines` (nested object - array of order lines)
        *   `item` (nested object)
        *   `quantity`
        *   `unit_cost`
        *   `amount`
        *   `description`
    *   `memo`
    *   `shipping_address` (nested object)
    *   `terms` (nested object)
    *   `created_at`
    *   `updated_at`

**6.5 Inventory Adjustments**

*   **QuickBooks Resource:** `conductor.qbd.inventory_adjustments`
*   **Django Model:**  (To be created - e.g., `InventoryAdjustment`)
*   **Fields to Sync:**
    *   `id`
    *   `transaction_date`
    *   `lines` (nested object - array of adjustment lines)
        *   `item` (nested object)
        *   `quantity_difference`
        *   `value_difference`
    *   `memo`
    *   `account` (nested object)

**6.6 Invoices**

*   **QuickBooks Resource:** `conductor.qbd.invoices`
*   **Django Model:** (To be created - e.g., `Invoice`)
*   **Fields to Sync (One-Way: QBD → WMS):**
    *   `id`
    *   `customer` (nested object)
    *   `transaction_date`
    *   `due_date`
    *   `total_amount`
    *   `balance_remaining`
    *   `is_paid`
    *   `lines` (nested object)
        *   `item` (nested object)
        *   `quantity`
        *   `unit_price`
        *   `amount`
    *   `billing_address` (nested object)
    *   `shipping_address` (nested object)
    *   `created_at`
    *   `updated_at`

**6.7 Vendors**
* **QuickBooks Resource:** `conductor.qbd.vendors`
* **Django Model:** `warehouse.models.Vendor`
* **Fields to Sync:**
    *   `id` (QuickBooks ID - primary key)
    *   `name`
    *   `company_name`
    *   `first_name`
    *   `last_name`
    *   `billing_address` (nested object - sync relevant fields like `line1`, `line2`, `city`, `state`, `postal_code`, `country`)
    *   `shipping_address` (nested object - same fields as billing_address)
    *   `phone`
    *   `email`
    *   `is_active`
    *   `created_at` (read-only from QuickBooks)
    *   `updated_at` (read-only from QuickBooks)
    *   `custom_fields` (if used - requires careful mapping)
    *   `balance` (read-only from QuickBooks)
    *   `total_balance` (read-only from QuickBooks)
    *   `currency`
    *   `terms` (nested object - sync `id` and `name`)

## Next Steps

1.  **Create/Update Models:**
    *   Create/update the `PurchaseOrder` model.
    *   Create an `InventoryAdjustment` model.
    *   Create an `Invoice` model.
    *   Replace the temporary `Product` model with specific item models (e.g., `InventoryItem`, `NonInventoryItem`, `ServiceItem`), inheriting from `ItemBase`.
2.  **Implement `SyncManager`:** Update the `admin_tools/quickbooks/sync_manager.py` file, removing references to the `ConductorClient` and initializing the `Conductor` client directly within the sync scripts.
3.  **Implement Individual Sync Scripts:** Create the sync scripts for each object type in `admin_tools/quickbooks/sync_scripts/`.
4.  **Update Views:** Modify the `admin_tools/quickbooks/views.py` to use the `SyncManager`. Specifically, update the `sync_progress` view to fetch detailed status information.
5.  **Update Templates:** Ensure the `admin_tools/templates/admin_tools/quickbooks/sync_dashboard.html` template correctly interacts with the updated views, using HTMX to poll for updates and display progress and errors. Also create/update the `sync_history.html` template.
6.  **Testing:** Thoroughly test the synchronization process, including error handling and conflict resolution.