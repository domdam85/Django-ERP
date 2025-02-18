from django.urls import path
from . import views

app_name = 'warehouse'

urlpatterns = [
    # Dashboard
    path('', views.home, name='home'),

    # Inventory
    path('inventory/', views.InventoryListView.as_view(), name='inventory-list'),
    path('inventory/create/', views.InventoryCreateView.as_view(), name='inventory-create'),
    path('inventory/<int:pk>/', views.InventoryDetailView.as_view(), name='inventory-detail'),
    path('inventory/<int:pk>/edit/', views.InventoryUpdateView.as_view(), name='inventory-update'),
    path('inventory/<int:pk>/delete/', views.InventoryDeleteView.as_view(), name='inventory-delete'),

    path('inventory/stats/', views.InventoryStatsView.as_view(), name='inventory-stats'),


    # Purchase Orders
    path('po/', views.po_list, name='po-list'),
    path('po/create/', views.po_create, name='po-create'),
    path('po/<int:pk>/', views.po_detail, name='po-detail'),
    path('po/<int:pk>/edit/', views.po_update, name='po-update'),
    path('po/<int:pk>/delete/', views.po_delete, name='po-delete'),
    path('po/<int:pk>/receive/', views.po_receive, name='po-receive'),
    path('po/<int:pk>/print/', views.po_print, name='po-print'),

    # Staging Areas
    path('staging/', views.staging_areas, name='staging-areas'),

    # Picking & Staging Views
    path('picking-lists/', views.picking_list, name='picking-list'),

    path('picking-lists/create/', views.create_pick_list, name='create-pick-list'),


    path('staging/create/', views.create_staging_area, name='staging-create'),
    path('staging/<int:pk>/edit/', views.edit_staging_area, name='staging-update'),
    path('staging/<int:pk>/delete/', views.delete_staging_area, name='staging-delete'),



    path('van-loading/staged-orders/', views.staged_orders, name='staged-orders'),

    # Van Loading Views
    path('van-loading/', views.van_loading, name='van-loading'),

    # Cycle Counts
    path('cycle-counts/', views.CycleCountListView.as_view(), name='cycle-count-list'),
    path('cycle-counts/create/', views.CycleCountCreateView.as_view(), name='cycle-count-create'),
    path('cycle-counts/<int:pk>/', views.CycleCountDetailView.as_view(), name='cycle-count-detail'),
    path('cycle-counts/<int:pk>/edit/', views.CycleCountUpdateView.as_view(), name='cycle-count-update'),
    path('cycle-counts/<int:pk>/start/', views.cycle_count_start, name='cycle-count-start'),
    path('cycle-counts/<int:pk>/complete/', views.cycle_count_complete, name='cycle-count-complete'),
    path('cycle-counts/<int:pk>/cancel/', views.cycle_count_cancel, name='cycle-count-cancel'),
    path('cycle-counts/<int:pk>/items/<int:item_pk>/', views.cycle_count_item_update, name='cycle-count-item-update'),
    path('cycle-counts/<int:pk>/report/', views.cycle_count_report, name='cycle-count-report'),

    # AJAX endpoints
    path('api/inventory-search/', views.inventory_search, name='inventory-search'),
    path('api/location-search/', views.location_search, name='location-search'),
]
