**FUNCTIONAL REQUIREMENTS DOCUMENT**

**WMS System for Wholesale Distribution with QuickBooks Desktop Integration**

**FINAL VERSION**

**Revised Complete Functional Design and Interface Overview**

**I. Functional Design Principles**

1.  **Domain-Centric Application Structure:** Sales, Delivery, Warehouse, Management, Admin.  Organize application features and interfaces into these core business domains for clarity and user focus.
2.  **Flexible User Access Model:** User-Level Staff flexible access to User Domains (Sales, Delivery, Warehouse); Manager to Management & User Domains; Admin to Admin, Management & User Domains.  Provide broad access for operational staff to user-level domains while restricting management and admin functions to appropriate roles.
3.  **Shared Route Concept:** Routes as location-based itineraries for Sales and Delivery. Utilize a shared 'Route' entity to manage sequences of stops for both sales representatives and delivery drivers, ensuring route consistency.
4.  **Tablet-Optimized User Interfaces (User Domains):** Tablet-first design for Sales, Delivery, and Warehouse domains, ensuring usability on mobile devices for field and warehouse staff.
5.  **Desktop-Optimized Management and Admin Panels (Management & Admin Domains):** Desktop-focused design for Management and Admin domains, optimized for data-rich views and administrative tasks best suited for larger screens.
6.  **Consistent Bootstrap 5 & HTMX UI Framework:** Implement a consistent user interface across all domains using Bootstrap 5 for responsive design and styling, and HTMX to enhance interactivity with minimal JavaScript, focusing on server-side rendering and dynamic updates.
7.  **QuickBooks Desktop Centric Design:** Design the application as an extension of QuickBooks Desktop, primarily leveraging QuickBooks data models and minimizing the creation of redundant custom data models. The system will synchronize seamlessly with QuickBooks Desktop to ensure data consistency and act as an operational front-end for QuickBooks data.
8.  **Automated Data Workflows:** Implement automated data flows to streamline business processes. Data should automatically progress through workflows (e.g., Sales Order -> Picking -> Loading -> Delivery) without manual intervention at each step, triggered by user actions within the system.

**II. User Roles and Responsibilities**

1.  **Admin (System Administrator):** Responsible for system configuration, QuickBooks integration management, user account management (system-level), data import/export, and overall technical maintenance of the WMS system.  Access to Admin and Management Domains.
2.  **Manager (Operations Manager, Route Planner, Warehouse Manager, etc.):** Responsible for business operations management, including route planning, driver and sales rep management, inventory oversight, procurement, and reporting. Access to Management and User Domains.
3.  **User (Staff User - Sales Rep, Delivery Driver, Warehouse Staff):** Responsible for executing daily operational tasks within their respective domains (Sales, Delivery, Warehouse). Flexible access to all User Domains to support various operational needs. Access to User Domains only.

**III. Interface Overview per Domain**

1.  **Sales Domain (Tablet Optimized - User Domain - Accessible to all User-Level Staff)**

    *   **Interface:** Tablet-optimized, Bootstrap 5 styled, HTMX-enhanced for dynamic interactions.
    *   **Target Users:** Sales Representatives (Primary), Delivery Drivers, Warehouse Staff (Secondary - flexible access).
    *   **Purpose:** Facilitate Sales Order taking while on customer routes and provide access to essential sales-related information directly from QuickBooks.
    *   **Dashboard: "Sales Dashboard"**:  (Tablet Optimized, Bootstrap 5, HTMX)
        *   Functionality: Display a summary of the day's sales route, key sales performance indicators (KPIs) derived from QuickBooks data, and quick action buttons.  HTMX will be used to dynamically update KPIs and route overviews.  Quick actions will include "Start Route," "View My Route," "Customer List," and "Item Catalog."
    *   **Left Navigation (Contextual User Domain Navigation - Bootstrap 5 Styled, HTMX):**  Bootstrap 5 styled sidebar navigation, dynamically updated via HTMX to reflect the Sales Domain context.
        *   Sales Dashboard (Link to `sales_dashboard_view`, Bootstrap Icon)
        *   My Route (Sales - Guided workflow for Sales Route - Link to `my_route_view_sales`, Bootstrap Icon)
        *   Sales Orders (View own Sales Orders - Link to `sales_order_list_view`, Bootstrap Icon)
        *   Customers (View assigned customers - view-only - Link to `customer_list_view_sales`, Bootstrap Icon)
        *   Item Catalog (View-only Item Catalog - Link to `item_catalog_view_sales`, Bootstrap Icon)
        *   Sales Reports (Personal Performance, Order History - Sales focused reports - Link to `sales_reports_view`, Bootstrap Icon)
    *   **Core Workflows and Interfaces (Bootstrap 5, HTMX Driven):**
        *   **"Start Route" View (`sales_dashboard_view` & `start_route_view`):** Bootstrap 5 button, enhanced with HTMX to initiate the Sales Route workflow.  Triggers server-side logic to prepare the route for the sales representative.
        *   **"My Route" View (`my_route_view_sales` & `my_route_sales.html` - Tablet Optimized List/Cards):** Bootstrap 5 list or card-based display of RouteStops for the assigned Sales Route. HTMX will dynamically load and update stop information. Each stop will include actions.
            *   **"Customer Detail" View (`customer_detail_view_sales` & `customer_detail_sales.html` - Bootstrap 5 Modal/Page):** Bootstrap 5 modal or page to display detailed customer information fetched from QuickBooks (address, contact, past orders - view only). Loaded dynamically via HTMX.
            *   **"Take Sales Order" View (`take_sales_order_view` & `take_sales_order_form.html` - Tablet Optimized Bootstrap 5 Form):** Tablet-optimized Bootstrap 5 form, enhanced with `django-crispy-forms`, to create a Sales Order for the selected customer. Item catalog access and dynamic price lookup (if feasible and beneficial) from QuickBooks will be implemented using HTMX. Quantity inputs and order notes are included.  Form submission via HTMX.
            *   **"Record Visit Note" (Optional):** Bootstrap 5 modal/form to add visit notes to the RouteStop, submitted via HTMX.
            *   **"Mark Stop Visited" (Within "My Route" Interface):** Bootstrap 5 checkbox or switch, updated via HTMX, to change the RouteStop status to 'Visited'.
            *   **"Complete Route" View (`complete_route_view` & `complete_route.html`):** Bootstrap 5 button, using HTMX to finalize the Sales Route upon completion, triggering server-side route completion processes.
        *   **"Sales Order List" View (`sales_order_list_view` & `sales_order_list.html` - Bootstrap 5 Table using `django-tables2`):** List of the sales representative's own Sales Orders, displayed in a Bootstrap 5 table using `django-tables2`. Filtering and searching will be implemented using HTMX to avoid full page reloads.
        *   **"Customer List" View (`customer_list_view_sales` & `customer_list_sales.html` - Bootstrap 5 Table using `django-tables2` - View Only):** Basic customer list (view-only for Sales context), displayed in a Bootstrap 5 table using `django-tables2`. Loaded via HTMX.
        *   **"Item Catalog" View (`item_catalog_view_sales` & `item_catalog_sales.html` - Bootstrap 5 Table using `django-tables2` - View Only):** Basic Item catalog (view-only for Sales context), displayed in a Bootstrap 5 table using `django-tables2`. Loaded and potentially filtered via HTMX.
        *   **"Sales Reports" View (`sales_reports_view` & `sales_reports.html` - Bootstrap 5 Table using `django-tables2`):** Basic sales performance reports (own orders summary), presented in Bootstrap 5 tables using `django-tables2`. Report data fetched and updated via HTMX.

2.  **Delivery Domain (Tablet Optimized - User Domain - Accessible to all User-Level Staff)**

    *   **Interface:** Tablet-optimized, Bootstrap 5 styled, HTMX-enhanced for dynamic van and route operations.
    *   **Target Users:** Delivery Drivers (Primary), Sales Representatives, Warehouse Staff (Secondary - flexible access).
    *   **Purpose:** Facilitate start-of-day van loading, delivery route execution, Proof of Delivery capture, end-of-day van unloading and returns processing, and provide delivery-related information, all tightly integrated with QuickBooks sales order and item data. Van operations are central to the Delivery Domain workflow.
    *   **Dashboard: "Delivery Dashboard"**: (Tablet Optimized, Bootstrap 5, HTMX)
        *   Functionality: Display today's delivery route overview, key delivery performance indicators (KPIs), and a prominent "Start Van Loading" button/section to emphasize the start-of-day van loading process. Quick actions will include "View My Route," and "Delivery Manifest." KPIs and route overviews dynamically updated via HTMX.
    *   **Left Navigation (Contextual User Domain Navigation - Bootstrap 5 Styled, HTMX):** Bootstrap 5 styled sidebar navigation, dynamically updated via HTMX to reflect the Delivery Domain context. "Van Operations" is a new top-level collapsible section to group van loading and unloading workflows.
        *   Delivery Dashboard (Link to `delivery_dashboard_view`, Bootstrap Icon)
        *   **Van Operations (New Top-Level Navigation - Bootstrap 5 Collapsible Section, HTMX-Enhanced):**
            *   Van Loading (Link to `van_loading_view`, Bootstrap Icon, HTMX) - Start-of-day van loading workflow.
            *   Van Unloading & Returns (Link to `van_unloading_view`, Bootstrap Icon, HTMX) - End-of-day van unloading and returns processing.
        *   My Route (Delivery - Link to `my_route_view_delivery`, Bootstrap Icon, HTMX)
        *   Delivery Manifest (Link to `delivery_manifest_view`, Bootstrap Icon, HTMX)
        *   Deliveries (Link to `delivery_list_view`, Bootstrap Icon, HTMX)
        *   Customers (View-Only - Link to `customer_list_view_delivery`, Bootstrap Icon, HTMX)
        *   Delivery Reports (Link to `delivery_reports_view`, Bootstrap Icon, HTMX)
    *   **Core Workflows and Interfaces (Bootstrap 5, HTMX Driven, Van Operations Integrated):**
        *   **"Van Loading" Workflow (`van_loading_view`, `van_loading.html`, `items_to_load_view`, `items_to_load.html`, `van_loading_item_confirm_view`, `van_loading_item_form.html`, `mark_van_loaded_view`, `mark_van_loaded.html` - Tablet Optimized Bootstrap 5 Interface):** Start-of-day van loading process, now a core workflow within the Delivery Domain. Accessed via "Van Operations" -> "Van Loading" in the navigation. All views and forms within this workflow will be Bootstrap 5 styled and utilize HTMX for dynamic updates.
            *   **"Van Loading Start" View (`van_loading_view` & `van_loading.html`):** Interface to select a van for loading. Uses a Bootstrap 5 Dropdown or List to choose a `VanInventory` van. Van selection and initial data loading via HTMX.
            *   **"Items to Load" View (`items_to_load_view` & `items_to_load.html` - Bootstrap 5 Table using `django-tables2` or Bootstrap 5 Cards/Lists):** Displays a list of items to be loaded onto the selected van. Sourced from completed Picking Lists assigned to the van's route (or van). Filtered to show only items ready for loading. Displayed in a Bootstrap 5 table using `django-tables2` or Bootstrap 5 cards/lists, dynamically loaded via HTMX.
            *   **"Loading Confirmation (Item by Item)" Workflow (`van_loading_item_confirm_view` & `van_loading_item_form.html` - Tablet Optimized Bootstrap 5 Form):** Interface to confirm the loading of each item onto the van. Tablet-optimized Bootstrap 5 form, enhanced with HTMX for item confirmation and dynamic updates to the loading list.
                *   **Barcode Scan Input (Optional):** Input field for optional item barcode scanning for verification, implemented with Bootstrap 5 styling.
                *   **"Confirm Load" Button (Bootstrap 5 Button):** Bootstrap 5 button to confirm loading of the current item. On submission (`van_loading_item_submit_view`), HTMX updates `VanInventory.quantity_on_hand` (increase) and `WarehouseInventory.quantity_on_hand` (decrease), reflecting the inventory movement. UI updated dynamically via HTMX.
            *   **"Mark Van Loaded" View (`mark_van_loaded_view` & `mark_van_loaded.html`):** "Mark Van Loaded" Bootstrap 5 button to finalize the van loading process. Triggering `mark_van_loaded_submit_view` updates `Van.status` to "Loaded" (or similar) and redirects to the Delivery Dashboard via HTMX.
        *   **"Van Unloading & Returns" Workflow (`van_unloading_view`, `van_unloading.html`, `record_van_return_view`, `record_van_return_form.html`, `complete_van_unloading_view`, `complete_van_unloading.html` - Tablet Optimized Bootstrap 5 Interface):** End-of-day van unloading and returns processing workflow. Accessible through "Van Operations" -> "Van Unloading & Returns." All views and forms within this workflow will be Bootstrap 5 styled and utilize HTMX for dynamic updates.
            *   **"Van Unloading Start" View (`van_unloading_view` & `van_unloading.html`):** Interface to select a van for unloading. Uses a Bootstrap 5 Dropdown or List to choose a `VanInventory` van. Van selection and initial data loading via HTMX.
            *   **"Record Returns from Van" Workflow (`record_van_return_view` & `record_van_return_form.html` - Tablet Optimized Bootstrap 5 Form):** Interface to record items returned from the van at the end of the delivery route. Tablet-optimized Bootstrap 5 form, enhanced with HTMX for dynamic item return recording.
                *   **Barcode Scan Input (Returned Item):** Input field for barcode scanning of returned items (or manual item selection), styled with Bootstrap 5.
                *   **"Quantity Returned" Input (Bootstrap 5 Number Input):** Bootstrap 5 number input field for `VanReturnItem.quantity_returned`.
                *   **"Reason for Return" Dropdown (Optional - Bootstrap 5 Dropdown):** Optional Bootstrap 5 dropdown (`CharField`) for `VanReturnItem.return_reason` (e.g., "Undeliverable," "Overstock," "Damaged").
                *   **"Record Return" Button (Bootstrap 5 Button):** Bootstrap 5 button to submit return information to `record_return_submit_view`. Saves `VanReturnItem` data and updates `VanInventory.quantity_on_hand` (decrease) and `WarehouseInventory.quantity_on_hand` (increase) via HTMX updates.
            *   **"Complete Van Unloading" View (`complete_van_unloading_view` & `complete_van_unloading.html`):** "Complete Van Unloading" Bootstrap 5 button to finalize the van unloading process. Triggers `complete_van_unloading_submit_view` to mark van unloading as "Complete" (updates van status - placeholder) and redirects to the Delivery Dashboard via HTMX.
        *   **"Start Route" View (`delivery_dashboard_view` & `start_route_view`):** Bootstrap 5 button, HTMX-enhanced, to initiate the Delivery Route execution workflow.
        *   **"My Route" View (Delivery) (`my_route_view_delivery` & `my_route_delivery.html` - Tablet Optimized List/Cards):** Delivery Route execution workflow, displayed as a tablet-optimized Bootstrap 5 list or card-based interface. Route stop information and actions dynamically loaded and updated via HTMX.
        *   **"Update Delivery Status" View (`update_delivery_status_view` & `update_delivery_status_form.html` - Tablet Optimized Bootstrap 5 Form for PoD):** Proof of Delivery (PoD) capture and delivery status updates. Tablet-optimized Bootstrap 5 form, submitted via HTMX to update delivery status and potentially capture signatures or photos (if needed).
        *   **"Delivery Manifest" View (`delivery_manifest_view` & `delivery_manifest.html` - Bootstrap 5 Table using `django-tables2` - View Only):** View-only delivery manifest for the current van, displayed in a Bootstrap 5 table using `django-tables2`. Data loaded via HTMX.
        *   **"Delivery List" View (`delivery_list_view` & `delivery_list.html` - Bootstrap 5 Table using `django-tables2`):** Basic list of deliveries for the current route, displayed in a Bootstrap 5 table using `django-tables2`. Filterable and searchable via HTMX.
        *   **"Customer List" View (Delivery) (`customer_list_view_delivery` & `customer_list_delivery.html` - Bootstrap 5 Table using `django-tables2` - View Only):** Basic customer list for delivery context (view-only), displayed in a Bootstrap 5 table using `django-tables2`. Loaded via HTMX.
        *   **"Delivery Reports" View (`delivery_reports_view` & `delivery_reports.html` - Bootstrap 5 Table using `django-tables2`):** Basic delivery performance reports, presented in Bootstrap 5 tables using `django-tables2`. Report data fetched and updated via HTMX.

3.  **Warehouse Domain (Tablet Optimized - User Domain - Accessible to all User-Level Staff)**

    *   **Interface:** Tablet-optimized, Bootstrap 5 styled, HTMX-enhanced for dynamic inventory and workflow management.
    *   **Target Users:** Warehouse Staff (Primary), Sales Representatives, Delivery Drivers (Secondary - flexible access).
    *   **Purpose:** Facilitate core warehouse operations including Receiving, Picking, Cycle Counting, and provide real-time warehouse inventory information synchronized from QuickBooks. Van Loading and Unloading workflows are now exclusively managed within the Delivery Domain.
    *   **Dashboard: "Warehouse Dashboard"**: (Tablet Optimized, Bootstrap 5, HTMX)
        *   Functionality: Display a warehouse status overview, a snapshot of current inventory levels, and quick action buttons for core warehouse tasks. Quick actions will include "Receive Stock," "View Picking Lists," and "Start Cycle Count." Dashboard elements dynamically updated via HTMX.
    *   **Left Navigation (Contextual User Domain Navigation - Bootstrap 5 Styled, HTMX):** Bootstrap 5 styled sidebar navigation, dynamically updated via HTMX to reflect the Warehouse Domain context. Van Operations links are removed from this domain's navigation.
        *   Warehouse Dashboard (Link to `warehouse_dashboard_view`, Bootstrap Icon, HTMX)
        *   Item Catalog (View-Only - Link to `item_catalog_view_warehouse`, Bootstrap Icon, HTMX)
        *   Warehouse Inventory (Link to `warehouse_inventory_view`, `initiate_cycle_count_view`, `pending_cycle_counts_view`, Bootstrap Icon, HTMX)
        *   Receiving (Link to `receive_stock_initiate_view`, `receiving_history_view`, Bootstrap Icon, HTMX)
        *   Picking (Link to `picking_lists_view`, `picking_history_view`, Bootstrap Icon, HTMX)
        *   **Van Inventory** (Link to `van_inventory_view`, Bootstrap Icon, HTMX - Van Inventory List remains for visibility, but Van Operations Management is in Delivery Domain)
        *   Inventory Reports (Link to `inventory_reports_view`, Bootstrap Icon, HTMX)
    *   **Core Workflows and Interfaces (Bootstrap 5, HTMX Driven, Van Operations Removed):**
        *   **"Receive Stock" Workflow (`receive_stock_initiate_view`, `receive_stock_initiate_form.html`, `display_po_details_view`, `po_details.html`, `receive_item_workflow_view`, `receive_item_form.html`, `complete_receiving_view`, `complete_receiving.html` - Tablet Optimized, Bootstrap 5 Forms and Views):** Guided workflow for receiving stock against Purchase Orders. Tablet-optimized Bootstrap 5 forms and views, with HTMX used for dynamic form updates, PO details loading, and workflow progression.
        *   **"Picking Orders" Workflow (`picking_lists_view`, `picking_lists.html`, `picking_workflow_view`, `picking_workflow.html`, `picking_workflow_item_form.html`, `complete_picking_list_view`, `complete_picking_list.html` - Tablet Optimized, Bootstrap 5 Tables and Forms):** Guided workflow for picking orders from Picking Lists. Tablet-optimized Bootstrap 5 tables and forms, with HTMX used to dynamically load picking lists, update picking status, and manage item picking confirmations.
        *   **"Cycle Count Workflow" View (`cycle_count_workflow_view`, `cycle_count_workflow.html`, `cycle_count_item_form.html` - Tablet Optimized Bootstrap 5 Forms):** Guided workflow for performing cycle counts. Tablet-optimized Bootstrap 5 forms, with HTMX used for dynamic item loading and cycle count updates.
        *   **"Warehouse Inventory" View (`warehouse_inventory_view` & `warehouse_inventory.html` - Bootstrap 5 Table using `django-tables2`):** View of current Warehouse Inventory, Initiate Cycle Count execution, View Pending Cycle Counts. Displayed in a Bootstrap 5 table using `django-tables2`. Inventory data and cycle count actions dynamically loaded and updated via HTMX.
        *   **"Receiving History" View (`receiving_history_view` & `receiving_history.html` - Bootstrap 5 Table using `django-tables2`):** History of Stock Receiving, displayed in a Bootstrap 5 table using `django-tables2`. History data loaded and filtered via HTMX.
        *   **"Picking History" View (`picking_history_view` & `picking_history.html` - Bootstrap 5 Table using `django-tables2`):** History of Order Picking, displayed in a Bootstrap 5 table using `django-tables2`. History data loaded and filtered via HTMX.
        *   **"Van Inventory" View (`van_inventory_view` & `van_inventory.html` - Bootstrap 5 Table using `django-tables2` - View of current Van Inventory - Remains for visibility, management in Delivery Domain).**  View of current Van Inventory levels, displayed in a Bootstrap 5 table using `django-tables2`. Data loaded via HTMX.

4.  **Management Domain (Desktop Optimized - Manager Domain - Restricted Access)**

    *   **(No changes in Management Domain Interface from example document)** - Remains as previously defined, desktop-optimized and Bootstrap 5 styled. HTMX can be incorporated for enhanced interactivity in future iterations if needed.
    *   **Interface:** Desktop-optimized, Bootstrap 5 styled.
    *   **Target Users:** Managers (Operations Managers, Route Planners, etc.).
    *   **Purpose:** Provide management oversight and control over all operational aspects of the WMS system, including item and customer management, route planning, procurement, inventory control, and reporting.
    *   **Dashboard: "Management Dashboard"**: Desktop Optimized, Bootstrap 5. Functionality: High-level overview of key operational metrics, alerts, and summaries across all domains.
    *   **Left Navigation (Manager Domain Navigation - Bootstrap 5 Styled):** Bootstrap 5 styled sidebar navigation for management functions.
        *   Management Dashboard (Link to `management_dashboard_view`, Bootstrap Icon)
        *   Item Catalog Management (Link to `item_management_view`, Bootstrap Icon)
        *   Customer Management (Link to `customer_management_view`, Bootstrap Icon)
        *   Route Management (Link to `route_management_view`, Bootstrap Icon)
        *   Driver Management (Link to `driver_management_view`, Bootstrap Icon)
        *   Procurement Management (Link to `procurement_management_view`, Bootstrap Icon)
        *   Inventory Management (Link to `inventory_management_view`, Bootstrap Icon)
        *   Reporting & Analytics (Link to `management_reports_view`, Bootstrap Icon)
    *   **Core Workflows and Interfaces (Bootstrap 5 Styled):**
        *   **"Management Dashboard" View (`management_dashboard_view` & `management_dashboard.html` - Desktop Optimized Bootstrap 5 Dashboard):** Centralized dashboard displaying key management information.
        *   **"Item Catalog Management" Views (`item_management_list_view`, `item_management_detail_view`, `item_create_view`, `item_update_view` etc. - Bootstrap 5 Tables and Forms):** CRUD (Create, Read, Update, Delete) interfaces for managing the Item Catalog, using Bootstrap 5 tables and forms.
        *   **"Customer Management" Views (`customer_management_list_view`, `customer_management_detail_view`, `customer_create_view`, `customer_update_view` etc. - Bootstrap 5 Tables and Forms):** CRUD interfaces for managing Customer data, using Bootstrap 5 tables and forms.
        *   **"Route Management" Views (`route_management_list_view`, `route_management_detail_view`, `route_create_view`, `route_update_view` etc. - Bootstrap 5 Tables, Forms, and potentially Map Views):** Interfaces for managing Routes, including route definition, stop assignment, and route optimization (if implemented), using Bootstrap 5 elements.
        *   **"Driver Management" Views (`driver_management_list_view`, `driver_management_detail_view`, `driver_create_view`, `driver_update_view` etc. - Bootstrap 5 Tables and Forms):** CRUD interfaces for managing Driver information, using Bootstrap 5 tables and forms.
        *   **"Procurement Management" Views (`procurement_management_list_view`, `procurement_management_detail_view`, `po_create_view`, `po_update_view`, `receive_stock_management_view` etc. - Bootstrap 5 Tables and Forms):** Interfaces for managing Procurement processes, including Purchase Order creation and management, and receiving oversight, using Bootstrap 5 elements.
        *   **"Inventory Management" Views (`inventory_management_dashboard_view`, `inventory_adjustments_view`, `warehouse_inventory_management_view`, `van_inventory_management_view` etc. - Bootstrap 5 Dashboards, Tables and Forms):** Interfaces for managing Inventory levels, performing adjustments, and viewing inventory status across warehouses and vans, using Bootstrap 5 elements.
        *   **"Reporting & Analytics" Views (`management_reports_view`, `sales_summary_report_view`, `delivery_performance_report_view`, `inventory_status_report_view` etc. - Bootstrap 5 Tables and Charts):** Interfaces for generating and viewing management reports and analytics dashboards, using Bootstrap 5 tables and basic charts.

5.  **Admin Domain (Desktop Optimized - Admin Domain - Re-skinned Django Admin - Restricted Access)**

    *   **(No changes in Admin Domain Interface from example document)** - Remains as previously defined, desktop-optimized and re-skinned Django Admin interface using Bootstrap 5.
    *   **Interface:** Desktop-optimized, Re-skinned Django Admin with Bootstrap 5 styling.
    *   **Target Users:** System Administrators (Admin Role).
    *   **Purpose:** System-level administration, technical configuration, and advanced data management.
    *   **Dashboard: "Admin Dashboard"**: Desktop Optimized, Re-skinned Django Admin, Bootstrap 5. Functionality: System status overview, quick access to administrative functions.
    *   **Left Navigation (Admin Domain Navigation - Re-skinned Django Admin, Bootstrap 5 Styled):** Re-skinned Django Admin sidebar navigation, Bootstrap 5 styled.
        *   Admin Dashboard (Link to Django Admin Dashboard, Bootstrap Icon)
        *   User Management (Link to Django Admin User Management, Bootstrap Icon)
        *   Group Management (Link to Django Admin Group Management, Bootstrap Icon)
        *   Data Management (Optional - Link to custom Django Admin-like data management views if needed, Bootstrap Icon)
        *   System Configuration (Future - Link to future system configuration panels, Bootstrap Icon)
        *   Django Admin Model Management (Links to standard Django Admin model management interfaces, Bootstrap Icon)
    *   **Core Workflows and Interfaces (Re-skinned Django Admin, Bootstrap 5 Styled):**
        *   **"Admin Dashboard" View (`admin_dashboard_view` & `admin_dashboard.html` - Re-skinned Django Admin Dashboard):** Re-skinned Django Admin dashboard, providing a system overview.
        *   **"User Management" Interfaces (Re-skinned Django Admin User Management Interfaces):** Standard Django Admin user management interfaces, re-skinned with Bootstrap 5.
        *   **"Group Management" Interfaces (Re-skinned Django Admin Group Management Interfaces):** Standard Django Admin group management interfaces, re-skinned with Bootstrap 5.
        *   **"Data Management" Interfaces (Optional - Custom Django Admin-like views for specific data management tasks):** Optional custom Django Admin-like views for specific data management tasks (e.g., data import/export), styled with Bootstrap 5.
        *   **"System Configuration" Interfaces (Future - Custom Django Admin-like configuration panels):** Future system configuration panels (e.g., QuickBooks integration settings), styled with Bootstrap 5.
        *   **"Django Admin Model Management" Interfaces (Standard Django Admin Model Management Interfaces):** Standard Django Admin model management interfaces for direct database model administration, re-skinned with Bootstrap 5.