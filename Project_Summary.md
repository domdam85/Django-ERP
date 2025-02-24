# **Final Project Summary & Implementation Guide**

## **1. Overall Vision**

- **Unified System:**  
  A single Django-based web application with a consistent look and feel, using responsive design (Bootstrap 5). All modules share a common navigation system with a collapsible, context-aware left nav that displays options relevant to the current domain (Sales, Delivery, Warehouse, Management, Purchasing).

- **Role-Based, Workflow-Driven Interfaces:**  
  Although all users have access to every module, each interface is designed with dedicated, sequential workflows to guide users step-by-step through their daily tasks.  
  - **Managers:** High-level dashboards of todays operations, route assignment and planning, inventory oversight, and robust analytics of sales, inventory, purchasing, and employee performance.
  - **Sales Representatives:** Route overview dashboard to review routes and stops, allows for manual re-organization (automated optimization in future). “Today’s Route” which is a guided customer visit workflow that presents the next customer stop with option for directions via googlemaps, at each stop driver can take notes or generate orders for this customer (may be multiple orders if multiple departments), sales rep must record some note for each stop to allow tracking their activity and time management, after submitting orders/notes or clicking "Finished" takes back to todays route with next stop queued up with option to map, etc. all steps in the workflow are available from the left nav but using "todays route" option will iterate through them populating the fields with relevant data.
  - **Delivery Representatives:** A guided, location-based workflow that leads drivers from one stop to the next, prompting them with a dedicated interface for each delivery step: arrival, scan/verify order, capture proof of delivery, handle exceptions (missing/damaged items, rejected items/orders) before moving on. Should functional similarly to sales route interface but for delivery functions.
  - **Warehouse Staff:** Step-by-step processes for receiving, picking, staging, loading, and cycle counting, with each task broken down into simple, sequential actions. Same as other apps but for warehouse functions.

- **QuickBooks Desktop Integration:**  
  Operational data (e.g., delivered orders and received purchase orders) is designed to eventually sync with QuickBooks Desktop using the QuickBooks Web Connector. For now, CSV import/export will simulate integration. Model mixins include fields (e.g., `qb_txn_id`, `qb_list_id`) to support this later.

---

## **2. Technical Stack**

### **Backend**
- **Framework:** Django (latest LTS)  
- **Database:** PostgreSQL (or SQLite for early development)  
- **API:** Django REST Framework (for future mobile endpoints or AJAX enhancements)  
- **Task Queue (Future):** Celery with Redis for background tasks (e.g., QB sync)  
- **Integration:** Custom modules for QuickBooks Desktop integration via the QuickBooks Web Connector (Phase 3)  
- **Data Import/Export:** CSV-based import/export utilities for testing QB data mapping

### **Frontend**
- **Templating:** Django Templates  
- **CSS Framework:** Bootstrap 5 (for responsive, consistent UI)  
- **JavaScript:** Minimal and only where needed. 
- **Navigation:** Top nav bar for navigating between business domain sections + a collapsible, context-aware left navigation panel that adapts to the current section.

### **Development Environment**
- **Windows 10:** Development PC with Python 3.12.8 venv configured and Postgressql available when needed

---

## **3. Django Project Architecture**

### **Repository Structure**

```
/Django-ERP (workspace)/
    manage.py
    /erp_system/         # Global configurations (settings, urls, wsgi)
    /warehouse/              # Warehouse operations: receiving, picking, staging, loading, cycle counts (all interfaces are tablet-optimized)
        models.py
        views.py
        urls.py
        templates/warehouse/...
    /sales/                  # Sales operations: guided stop-to-stop sales process, sales order and note creation at each stop (all interfaces are tablet-optimized)
        models.py
        views.py
        urls.py
        templates/sales/...
    /delivery/               # Delivery operations: guided stop-to-stop delivery process, proof-of-delivery capture, exception reporting (all interfaces are tablet-optimized)
        models.py
        views.py
        urls.py
        templates/delivery/...
    /management/             # Management module (desktop-oriented interfaces):
                             # - Operational dashboards, route management (drag-and-drop planner, detailed logs)
                             # - Procurement functions (demand forecasting, vendor purchase order generation, re-order point recommendations)
        models.py
        views.py
        urls.py
        templates/management/...
    /admin_tools/        # Admin dashboard for system-level configurations and django management (desktop-oriented interfaces):
                             # - User management, CSV import with data mapping, later to be extended to provide integration configuration (QuickBooks Desktop integration via QBWC)
                             #   and audit/log review with change approval.
        models.py
        views.py
        urls.py
        templates/admin_dashboard/...
    /common/                 # Shared utilities, helper functions
        utils.py
        models.py (if needed)
        templates/...


### **Unified & Context-Aware Navigation**
- **Base Template (`base.html`):**  
  - Incorporates a **collapsible left navigation panel** that dynamically adapts:
    - **Sales Module:** “Today’s Route,”, “New Order,” “Customer CRM.”
    - **Warehouse Module:** “Receive Inventory,” “Pick & Stage,” “Van Loading,” “Cycle Counting.”
    - **Delivery Module:** “Today’s Route,” “Delivery Verification,” “Exception Reporting.”
    - **Management Module:** “Dashboard Overview,” “Route Management,” “Operational Reports,” and cross-domain monitoring tools.
    - **Purchasing Module:** “Procurement Wizard,” “Analytics Dashboard.”
    - **Admin Dashboard:** Accessed separately by sysadmin for system configurations, user management, and integrations.

---

## **4. Detailed Workflow & Interface Specifications**

### **A. Manager (Business Operations) Interface**
High-level dashboards of todays operations, route assignment and planning, inventory oversight, and robust analytics of: sales, inventory, purchasing, and employee performance.
#### **Key Tasks:**
- **Oversee All Business Domains:**  
  - Monitor real-time operations across Sales, Delivery, Warehouse, and Purchasing.
  - View summary dashboards and detailed reports for each domain.
- **Analytics:**  
  - Access interactive analytics charts for inventory turnover, item sales trends, customer purchasing trends, customer churn warnings.  
- **Route Management:**  
  - Use interactive dashboards to manage routes: customer route assignment, route day assignment, route rep assignment. Overview of route status (progress), live delivery statuses (orders), and van inventory summaries (items scanned on are scanned off or manually checked off), a drag-and-drop route planner for assigning and rearranging customer stops.

- **Cross-Domain Monitoring:**  
  - View high-level performance metrics for Sales (orders taken, revenue), Delivery (successful deliveries, exceptions), Warehouse (inventory recieved, picked- staged, cycle counts), and Purchasing (procurement status, cost trends).

#### **Workflow & UI:**
- **Dashboard Screen:**  
  - Consolidated view with separate widgets for each functional domain.
  - Drill-down capabilities: clicking a widget reveals detailed views specific to that domain.
- **Route Planning & Operations Panel:**  
  - A drag-and-drop interface for route planning.
  - Detailed logs of order processing and inventory movements.

---

### **B. Sales Representative Interface**

#### **Key Tasks:**
- **Guided Customer Visits & Order Taking:**  
  - Follow a “Today’s Route” that guides the sales rep from one customer stop to the next.
  - Step-by-step order entry with minimal data entry and error reduction.
- **CRM & Follow-Up:**  
  - Log customer interactions with simple note-taking and follow-up flagging.

#### **Workflow & UI:**
- **“Today’s Route” Screen:**  
  - Prominently displays the next customer stop with map details and directions.
  - A “Begin Order Entry” button initiates the dedicated order entry process.
- **Order Entry Wizard:**  
  - Step 1: Confirm customer details (auto-populated).
  - Step 2: Select products using search or barcode scanning.
  - Step 3: Adjust quantities, review order, and submit.
  - Immediate feedback upon order submission.
- **CRM Interaction Screen:**  
  - A dedicated space to log interactions with quick “Call,” “Email,” or “Follow-Up” buttons.

---

### **C. Delivery Representative Interface**

#### **Key Tasks:**
- **Guided Delivery Process:**  
  - Navigate through stops sequentially, with the system guiding the driver from one delivery to the next.
  - For each stop, a dedicated interface prompts the driver through the delivery steps: arrival, order verification, proof-of-delivery capture, and exception reporting.
- **Van Loading Verification:**  
  - A separate guided interface to confirm loading of orders into the delivery van at the start of the day.

#### **Workflow & UI:**
- **Next Stop Screen:**  
  - Displays the next delivery stop with customer name, address, and map/directions.
  - A “Begin Delivery” button transitions to the delivery workflow.
- **Delivery Verification Screen:**  
  - **Step 1: Order Verification:**  
    - A large “Scan Order” button with a live camera feed (fallback to manual entry).
    - Product list with checkboxes that automatically check off upon successful scanning.
  - **Step 2: Proof-of-Delivery Capture:**  
    - A dedicated area to capture a digital signature, take a photo, or automatically record geo-location and timestamp.
  - **Step 3: Exception Reporting:**  
    - If a delivery cannot be completed or an item is omitted from a delivery, provide a clear, step-by-step exception reporting process with a dropdown of common reasons and an optional comment field.
  - **Post-Delivery Confirmation:**  
    - After completing a stop, a confirmation dialog prompts the driver to proceed to the next stop showing the Next Stop Screen.
- **Van Loading Workflow:**  
  - A guided interface to scan and confirm each order is loaded into the van, with a final summary confirmation.

---

### **D. Warehouse Staff Interface**

#### **Key Tasks:**
- **Receiving Inventory:**  
  - Process incoming shipments by selecting Purchase Order from interface and begin scanning products, with clear prompts for handling discrepancies. This generates an ItemReceipt which is synchronized with Quickbooks.
- **Order Picking & Staging:**  
  - Use a bulk scanning workflow for multiple orders grouped by delivery routes, with visible checklists and progress indicators.
- **Cycle Counting:**  
  - Perform cycle counts by scanning warehouse zones and products, entering counts, and flagging discrepancies.
- **Van Loading Verification:**  
  - Confirm that orders are loaded onto the correct delivery van via a guided scanning process.

#### **Workflow & UI:**
- **Receiving Screen:**  
  - A prominent button to scan or enter a PO, displaying expected products and quantities.
  - A “Confirm Receipt” button finalizes the inventory update.
- **Picking & Staging Screen:**  
  - A unified list view grouped by delivery route.
  - Bulk-scan functionality with checklists and a “Stage for Loading” button.
- **Cycle Counting Screen:**  
  - Sequential interface for selecting a warehouse zone, scanning products, entering counts, and flagging issues.
- **Van Loading Screen:**  
  - A dedicated screen for scanning orders into the van, with a summary confirmation at the end.

---

### **E. Admin Dashboard (System-Level Configurations)**

#### **Key Tasks:**
- **System Configuration & Integrations:**  
  - Manage user accounts, roles, and permissions.
  - Configure integrations (e.g., QuickBooks Desktop, external APIs).
  - Monitor background tasks, logs, and system health.
- **Global Settings & Audit Trails:**  
  - Set and manage global application settings.
  - Access audit logs for all operational activities.
  - Oversee and troubleshoot synchronization processes with QuickBooks Desktop.

#### **Workflow & UI:**
- **Dashboard Screen:**  
  - A clear overview of system usage, integration status, last sync time, any errors  
- **User & Role Management Panel:**  
  - Tools for creating, editing, and managing user accounts and their permissions.
- **Integration & Settings Panel:**  
  - Interfaces for configuring integrations (e.g., Conductor API Key and End User ID settings, auto-sync scheduling, conflict resolution settings, etc.) and managing system-wide configurations.
- **Audit & Log Viewer:**  
  - A searchable, filterable interface for reviewing system audit trails and background task logs.

---

## **5. QuickBooks Desktop Integration Details**

- **Data Types That Need Synchronization:**
 - Data Type	Sync Direction	Reasoning
 - Items (All Types)	Bidirectional	Needed for invoices, sales orders, purchase orders, etc.
 - Customers	Bidirectional	Ensures accurate customer records in both systems. - 
 - Vendors	Bidirectional	Needed for purchase orders and stock replenishment.
 - Sales Orders	Bidirectional	Allows WMS to process orders while QBD handles invoices.
 - Invoices	One-Way (QBD → WMS)	Prevents accidental financial data modification by WMS users.
 - Purchase Orders	Bidirectional	Needed for accurate stock tracking and supplier management.
 - Inventory Adjustments	Bidirectional	Ensures accurate stock levels in both systems.

- **Data Flow (Bidirectional vs. One-Way):**
 - Bidirectional Sync (for operational data) ensures real-time accuracy in both systems.
 - One-Way Sync (QBD → WMS) for financial data prevents unauthorized edits in WMS.

- **Scenario	Sync Direction	Implementation Notes:**
 - A new item is added in WMS	WMS → QBD	Conductor API creates item in QBD.
 - A new item is added in QBD	QBD → WMS	Conductor API syncs item to WMS.
 - Sales order is created in WMS	WMS → QBD	Ensures accounting records match.
 - QuantityOnHand is in WMS & QBD	WMS / QBD	Stock levels do not sync, they are managed independently in both systems to isolate discrepancies.
 - An invoice is generated in QBD	QBD → WMS	Read-only sync to WMS (no editing in WMS).
 - 3Conflict Resolution Strategy

- **Since we sync hourly, conflicts are rare, but we need rules for when they happen.:**
 - Conflict Type	Resolution Strategy
 - Item updated in both QBD & WMS	Latest timestamp wins.
 - Customer modified in both QBD & WMS	QBD is authoritative (unless only WMS changed contact details).
 - Inventory adjusted in both QBD & WMS	Calculate the net change and update accordingly.
 - Sales Order modified in both systems	WMS is authoritative (since fulfillment happens there).


---

## **6. Phased Development Roadmap**

### **Phase 1 (MVP – Core Functionality)**
- **Setup & Environment:**  
  - Initialize the Django project (with PostgreSQL/SQLite), configure virtual environments, install Bootstrap 5, and set up base templates with a collapsible, context-aware left navigation.
- **Core Models & CRUD Operations:**  
  - Develop models for users, sales orders, purchase orders, inventory items, delivery records, and include QB integration fields.
- **Module-Specific Workflows:**  
  - **Warehouse Module:** Implement receiving, picking/staging, van loading, and cycle counting screens.
  - **Sales Module:** Build the “Today’s Route” view and guided order entry process.
  - **Delivery Module:** Create a sequential, guided delivery workflow (next stop, order verification, proof-of-delivery capture, exception handling) and van loading verification.
  - **Management Module:** Develop a dashboard with cross-domain oversight, route planning, operational reports, and purchasing analytics.
  - **Admin Tools:** Build system-level interfaces for user management, integration settings, and audit/log review and approval interface for certain operations (Phase 2 enhancement)
- **CSV Import/Export Utilities:**  
  - Create utilities to simulate QuickBooks Desktop integration for testing.
- **Testing & Iteration:**  
  - Conduct unit tests, user testing sessions, and refine UI/UX based on feedback.

### **Phase 2: UI Enhancements & Real-Time Features**
- Refine and optimize UI/UX across all modules.
- Implement features designated for phase 2
- Enhance analytics dashboards with more interactive charts and data.

### **Phase 3: QuickBooks Desktop Integration**
- Utilize Conductor API to simplify integration with Quickbooks Desktop
- Implement background synchronization tasks with Celery.
- Thoroughly test data integrity between the operational system and QuickBooks Desktop.

---

# **Final Summary**

This enhanced design ensures:
- **System Administrators** access a separate Admin Dashboard for configurations, integrations, user management, and audit/log tracking, approval workflows for data changes.
- **Managers** have a comprehensive operational oversight interface that spans all business domains (Sales, Delivery, Warehouse, Purchasing) while remaining distinct from system-level functions.
- **Workflow-Driven Interfaces** guide users (Sales, Delivery, Warehouse) through clear, step-by-step processes to reduce errors and enforce business protocols.
- **A Unified, Responsive Application** using Django, Bootstrap 5, and a context-aware collapsible left navigation that adapts based on the active module.
- **Future-Proof Data Models** include fields for QuickBooks Desktop integration, with CSV import/export for Phase 1 and a dedicated integration module planned for Phase 3.