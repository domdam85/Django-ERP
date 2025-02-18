from django.db import models

class ItemBase(models.Model): # Abstract base model for common item fields
    list_id = models.CharField(max_length=255, primary_key=True, verbose_name="List ID")
    time_created = models.DateTimeField(null=True, blank=True, verbose_name="Time Created")
    time_modified = models.DateTimeField(null=True, blank=True, verbose_name="Time Modified")
    edit_sequence = models.CharField(max_length=255, verbose_name="Edit Sequence")
    name = models.CharField(max_length=255, verbose_name="Name")
    full_name = models.CharField(max_length=255, verbose_name="Full Name")
    bar_code_value = models.CharField(max_length=255, blank=True, null=True, verbose_name="Bar Code Value")
    is_active = models.BooleanField(null=True, blank=True, verbose_name="Is Active")
    class_ref_list_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="Class Ref List ID")
    class_ref_full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Class Ref Full Name")
    parent_ref_list_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="Parent Ref List ID")
    parent_ref_full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Parent Ref Full Name")
    sublevel = models.IntegerField(verbose_name="Sublevel") # Sublevel is required in all ItemRet types
    unit_of_measure_set_ref_list_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="Unit Of Measure Set Ref List ID")
    unit_of_measure_set_ref_full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Unit Of Measure Set Ref Full Name")
    is_tax_included = models.BooleanField(null=True, blank=True, verbose_name="Is Tax Included")
    sales_tax_code_ref_list_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="Sales Tax Code Ref List ID")
    sales_tax_code_ref_full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Sales Tax Code Ref Full Name")
    external_guid = models.CharField(max_length=255, blank=True, null=True, verbose_name="External GUID")
    item_type_qbxml = models.CharField(max_length=255, blank=True, null=True, verbose_name="Item Type QBXML") # To store QBXML Item Type

    quickbooks_sync_token = models.IntegerField(null=True, blank=True)
    last_synced_datetime = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.full_name

# Temporary models to maintain compatibility with existing views
class Product(ItemBase):
    """
    Temporary model to maintain compatibility with existing views.
    This will be replaced with proper QuickBooks item models.
    """
    sku = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    reorder_point = models.IntegerField(default=0)
    location = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

class ItemDataExtRet(models.Model):
    """
    Temporary model to maintain compatibility with existing views.
    This will be replaced with proper QuickBooks data extension functionality.
    """
    item = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='data_ext_ret', verbose_name="Item")
    owner_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="Owner ID")
    data_ext_name = models.CharField(max_length=255, verbose_name="Data Ext Name")
    data_ext_type = models.CharField(max_length=255, verbose_name="Data Ext Type")
    data_ext_value = models.TextField(verbose_name="Data Ext Value")
    quickbooks_sync_token = models.IntegerField(null=True, blank=True)
    last_synced_datetime = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"DataExt for {self.item.full_name}: {self.data_ext_name}"

class ItemService(ItemBase):
    sales_or_purchase_choice = models.CharField(max_length=50, choices=[('SalesOrPurchase', 'SalesOrPurchase'), ('SalesAndPurchase', 'SalesAndPurchase')], blank=True, null=True)

    sales_or_purchase_desc = models.TextField(blank=True, null=True, verbose_name="Sales Or Purchase Desc")
    sales_or_purchase_price = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Sales Or Purchase Price")
    sales_or_purchase_price_percent = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Sales Or Purchase Price Percent")

    sales_and_purchase_sales_desc = models.TextField(blank=True, null=True, verbose_name="Sales And Purchase Sales Desc")
    sales_and_purchase_sales_price = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Sales And Purchase Sales Price")
    sales_and_purchase_purchase_desc = models.TextField(blank=True, null=True, verbose_name="Sales And Purchase Purchase Desc")
    sales_and_purchase_purchase_cost = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Sales And Purchase Purchase Cost")
    sales_and_purchase_purchase_tax_code_ref_list_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="Sales And Purchase Purchase Tax Code Ref List ID")
    sales_and_purchase_purchase_tax_code_ref_full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Sales And Purchase Purchase Tax Code Ref Full Name")
    sales_and_purchase_pref_vendor_ref_list_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="Sales And Purchase Pref Vendor Ref List ID")
    sales_and_purchase_pref_vendor_ref_full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Sales And Purchase Pref Vendor Ref Full Name")


class ItemNonInventory(ItemBase):
    manufacturer_part_number = models.CharField(max_length=255, blank=True, null=True, verbose_name="Manufacturer Part Number")
    sales_or_purchase_choice = models.CharField(max_length=50, choices=[('SalesOrPurchase', 'SalesOrPurchase'), ('SalesAndPurchase', 'SalesAndPurchase')], blank=True, null=True)

    sales_or_purchase_desc = models.TextField(blank=True, null=True, verbose_name="Sales Or Purchase Desc")
    sales_or_purchase_price = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Sales Or Purchase Price")
    sales_or_purchase_price_percent = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Sales Or Purchase Price Percent")

    sales_and_purchase_sales_desc = models.TextField(blank=True, null=True, verbose_name="Sales And Purchase Sales Desc")
    sales_and_purchase_sales_price = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Sales And Purchase Sales Price")
    sales_and_purchase_purchase_desc = models.TextField(blank=True, null=True, verbose_name="Sales And Purchase Purchase Desc")
    sales_and_purchase_purchase_cost = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Sales And Purchase Purchase Cost")
    sales_and_purchase_purchase_tax_code_ref_list_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="Sales And Purchase Purchase Tax Code Ref List ID")
    sales_and_purchase_purchase_tax_code_ref_full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Sales And Purchase Purchase Tax Code Ref Full Name")
    sales_and_purchase_pref_vendor_ref_list_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="Sales And Purchase Pref Vendor Ref List ID")
    sales_and_purchase_pref_vendor_ref_full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Sales And Purchase Pref Vendor Ref Full Name")


class ItemOtherCharge(ItemBase):
    special_item_type = models.CharField(max_length=255, blank=True, null=True, verbose_name="Special Item Type")
    sales_or_purchase_choice = models.CharField(max_length=50, choices=[('SalesOrPurchase', 'SalesOrPurchase'), ('SalesAndPurchase', 'SalesAndPurchase')], blank=True, null=True)

    sales_or_purchase_desc = models.TextField(blank=True, null=True, verbose_name="Sales Or Purchase Desc")
    sales_or_purchase_price = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Sales Or Purchase Price")
    sales_or_purchase_price_percent = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Sales Or Purchase Price Percent")

    sales_and_purchase_sales_desc = models.TextField(blank=True, null=True, verbose_name="Sales And Purchase Sales Desc")
    sales_and_purchase_sales_price = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Sales And Purchase Sales Price")
    sales_and_purchase_purchase_desc = models.TextField(blank=True, null=True, verbose_name="Sales And Purchase Purchase Desc")
    sales_and_purchase_purchase_cost = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Sales And Purchase Purchase Cost")
    sales_and_purchase_purchase_tax_code_ref_list_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="Sales And Purchase Purchase Tax Code Ref List ID")
    sales_and_purchase_purchase_tax_code_ref_full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Sales And Purchase Purchase Tax Code Ref Full Name")
    sales_and_purchase_pref_vendor_ref_list_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="Sales And Purchase Pref Vendor Ref List ID")
    sales_and_purchase_pref_vendor_ref_full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Sales And Purchase Pref Vendor Ref Full Name")


class ItemInventory(ItemBase):
    manufacturer_part_number = models.CharField(max_length=255, blank=True, null=True, verbose_name="Manufacturer Part Number")
    sales_desc = models.TextField(blank=True, null=True, verbose_name="Sales Desc")
    sales_price = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Sales Price")
    purchase_desc = models.TextField(blank=True, null=True, verbose_name="Purchase Desc")
    purchase_cost = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Purchase Cost")
    purchase_tax_code_ref_list_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="Purchase Tax Code Ref List ID")
    purchase_tax_code_ref_full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Purchase Tax Code Ref Full Name")
    pref_vendor_ref_list_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="Pref Vendor Ref List ID")
    pref_vendor_ref_full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Pref Vendor Ref Full Name")
    reorder_point = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Reorder Point")
    max_level = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Max Level")
    quantity_on_hand = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Quantity On Hand")
    average_cost = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Average Cost")
    quantity_on_order = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Quantity On Order")
    quantity_on_sales_order = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Quantity On Sales Order")


class ItemInventoryAssembly(ItemBase):
    manufacturer_part_number = models.CharField(max_length=255, blank=True, null=True, verbose_name="Manufacturer Part Number")
    sales_desc = models.TextField(blank=True, null=True, verbose_name="Sales Desc")
    sales_price = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Sales Price")
    purchase_desc = models.TextField(blank=True, null=True, verbose_name="Purchase Desc")
    purchase_cost = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Purchase Cost")
    purchase_tax_code_ref_list_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="Purchase Tax Code Ref List ID")
    purchase_tax_code_ref_full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Purchase Tax Code Ref Full Name")
    pref_vendor_ref_list_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="Pref Vendor Ref List ID")
    pref_vendor_ref_full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Pref Vendor Ref Full Name")
    build_point = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Build Point")
    max_level = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Max Level")
    quantity_on_hand = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Quantity On Hand")
    average_cost = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Average Cost")
    quantity_on_order = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Quantity On Order")
    quantity_on_sales_order = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Quantity On Sales Order")


class ItemFixedAsset(ItemBase):
    acquired_as = models.CharField(max_length=255, verbose_name="Acquired As") # Required field
    purchase_desc = models.TextField(verbose_name="Purchase Desc") # Required field
    purchase_date = models.DateField(verbose_name="Purchase Date") # Required field
    purchase_cost = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Purchase Cost")
    vendor_or_payee_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Vendor Or Payee Name")
    fixed_asset_sales_desc = models.TextField(verbose_name="Fixed Asset Sales Desc") # Required field in FixedAssetSalesInfo
    fixed_asset_sales_date = models.DateField(verbose_name="Fixed Asset Sales Date") # Required field in FixedAssetSalesInfo
    fixed_asset_sales_price = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Fixed Asset Sales Price")
    fixed_asset_sales_expense = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Fixed Asset Sales Expense")
    asset_desc = models.CharField(max_length=255, blank=True, null=True, verbose_name="Asset Desc")
    location = models.CharField(max_length=255, blank=True, null=True, verbose_name="Location")
    po_number = models.CharField(max_length=255, blank=True, null=True, verbose_name="PO Number")
    serial_number = models.CharField(max_length=255, blank=True, null=True, verbose_name="Serial Number")
    warranty_exp_date = models.DateField(null=True, blank=True, verbose_name="Warranty Exp Date")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    asset_number = models.CharField(max_length=255, blank=True, null=True, verbose_name="Asset Number")
    cost_basis = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Cost Basis")
    year_end_accumulated_depreciation = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Year End Accumulated Depreciation")
    year_end_book_value = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Year End Book Value")


class ItemSubtotal(ItemBase):
    special_item_type = models.CharField(max_length=255, blank=True, null=True, verbose_name="Special Item Type")
    item_desc = models.CharField(max_length=255, blank=True, null=True, verbose_name="Item Desc")


class ItemDiscount(ItemBase):
    item_desc = models.CharField(max_length=255, blank=True, null=True, verbose_name="Item Desc")
    discount_rate = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Discount Rate")
    discount_rate_percent = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Discount Rate Percent")


class ItemPayment(ItemBase):
    item_desc = models.CharField(max_length=255, blank=True, null=True, verbose_name="Item Desc")
    payment_method_ref_list_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="Payment Method Ref List ID")
    payment_method_ref_full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Payment Method Ref Full Name")


class ItemSalesTax(ItemBase):
    item_desc = models.CharField(max_length=255, blank=True, null=True, verbose_name="Item Desc")
    tax_rate = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Tax Rate")
    tax_vendor_ref_list_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tax Vendor Ref List ID")
    tax_vendor_ref_full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tax Vendor Ref Full Name")
    sales_tax_return_line_ref_list_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="Sales Tax Return Line Ref List ID")
    sales_tax_return_line_ref_full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Sales Tax Return Line Ref Full Name")


class ItemSalesTaxGroup(ItemBase):
    item_desc = models.CharField(max_length=255, blank=True, null=True, verbose_name="Item Desc")


class ItemGroup(ItemBase):
    item_desc = models.CharField(max_length=255, blank=True, null=True, verbose_name="Item Desc")
    is_print_items_in_group = models.BooleanField(null=True, blank=True, verbose_name="Is Print Items In Group")
    special_item_type = models.CharField(max_length=255, blank=True, null=True, verbose_name="Special Item Type")


class ItemInventoryAssemblyLine(models.Model):
    assembly_item = models.ForeignKey(ItemInventoryAssembly, on_delete=models.CASCADE, related_name='assembly_lines', verbose_name="Assembly Item")
    item_inventory_ref_list_id = models.CharField(max_length=255, verbose_name="Item Inventory Ref List ID")
    item_inventory_ref_full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Item Inventory Ref Full Name")
    quantity = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Quantity") # Quantity is optional in schema
    item_line_number = models.IntegerField(verbose_name="Item Line Number") # Added for sequence

    quickbooks_sync_token = models.IntegerField(null=True, blank=True)
    last_synced_datetime = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('assembly_item', 'item_line_number')

    def __str__(self):
        return f"Line for {self.assembly_item.full_name}: {self.item_inventory_ref_full_name} - Qty {self.quantity}"


class ItemGroupLine(models.Model):
    group_item = models.ForeignKey(ItemGroup, on_delete=models.CASCADE, related_name='group_lines', verbose_name="Group Item")
    item_ref_list_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="Item Ref List ID (Group Line)")
    item_ref_full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Item Ref Full Name (Group Line)")
    quantity = models.DecimalField(max_digits=19, decimal_places=5, null=True, blank=True, verbose_name="Quantity (Group Line)") # Quantity is optional in schema
    unit_of_measure = models.CharField(max_length=255, blank=True, null=True, verbose_name="Unit of Measure (Group Line)")
    item_line_number = models.IntegerField(verbose_name="Item Line Number") # Added for sequence

    class Meta:
        unique_together = ('group_item', 'item_line_number')

    def __str__(self):
        return f"Line for {self.group_item.full_name}: {self.item_ref_full_name} - Qty {self.quantity}"

class Vendor(ItemBase):
    """
    Temporary model to maintain compatibility with existing views.
    This will be replaced with proper QuickBooks vendor model.
    """
    class Meta:
        verbose_name = 'Vendor'
        verbose_name_plural = 'Vendors'

class PurchaseOrder(models.Model):
    """
    Temporary model to maintain compatibility with existing views.
    This will be replaced with proper QuickBooks purchase order model.
    """
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    po_number = models.CharField(max_length=50, unique=True)
    order_date = models.DateField()
    expected_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=50, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Purchase Order'
        verbose_name_plural = 'Purchase Orders'

    def __str__(self):
        return f"PO-{self.po_number} ({self.vendor})"

class POItem(models.Model):
    """
    Temporary model to maintain compatibility with existing views.
    This will be replaced with proper QuickBooks purchase order line item model.
    """
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ordered_quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Purchase Order Item'
        verbose_name_plural = 'Purchase Order Items'

    def __str__(self):
        return f"{self.product} x {self.ordered_quantity} (PO: {self.purchase_order.po_number})"

class ReceiptLog(models.Model):
    """
    Temporary model to maintain compatibility with existing views.
    This will be replaced with proper QuickBooks receipt model.
    """
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE)
    receipt_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Receipt Log'
        verbose_name_plural = 'Receipt Logs'

class ReceiptItem(models.Model):
    """
    Temporary model to maintain compatibility with existing views.
    This will be replaced with proper QuickBooks receipt line item model.
    """
    receipt = models.ForeignKey(ReceiptLog, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    class Meta:
        verbose_name = 'Receipt Item'
        verbose_name_plural = 'Receipt Items'

class AggregatedPickList(models.Model):
    """
    Temporary model to maintain compatibility with existing views.
    This will be replaced with proper picking functionality.
    """
    delivery_route = models.CharField(max_length=100)
    delivery_date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='pending')

    class Meta:
        verbose_name = 'Aggregated Pick List'
        verbose_name_plural = 'Aggregated Pick Lists'

    def __str__(self):
        return f"Pick List for {self.delivery_route} on {self.delivery_date}"

class PickListItem(models.Model):
    """
    Temporary model to maintain compatibility with existing views.
    This will be replaced with proper picking functionality.
    """
    pick_list = models.ForeignKey(AggregatedPickList, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    class Meta:
        verbose_name = 'Pick List Item'
        verbose_name_plural = 'Pick List Items'

class StagingArea(models.Model):
    """
    Temporary model to maintain compatibility with existing views.
    This will be replaced with proper staging functionality.
    """
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=50, default='active')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Staging Area'
        verbose_name_plural = 'Staging Areas'

    def __str__(self):
        return self.name

class StagedOrder(models.Model):
    """
    Temporary model to maintain compatibility with existing views.
    This will be replaced with proper staging functionality.
    """
    staging_area = models.ForeignKey(StagingArea, on_delete=models.CASCADE)
    pick_list = models.ForeignKey(AggregatedPickList, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)
    staged_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='staged')

    class Meta:
        verbose_name = 'Staged Order'
        verbose_name_plural = 'Staged Orders'

    def __str__(self):
        return f"Order staged at {self.staging_area} ({self.staged_at})"

class Backorder(models.Model):
    """
    Temporary model to maintain compatibility with existing views.
    This will be replaced with proper backorder functionality.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Backorder'
        verbose_name_plural = 'Backorders'

class CycleCount(models.Model):
    """
    Temporary model to maintain compatibility with existing views.
    This will be replaced with proper cycle count functionality.
    """
    zone = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='pending')

    class Meta:
        verbose_name = 'Cycle Count'
        verbose_name_plural = 'Cycle Counts'

    def __str__(self):
        return f"Cycle Count {self.zone} ({self.created_at})"

class CycleCountItem(models.Model):
    """
    Temporary model to maintain compatibility with existing views.
    This will be replaced with proper cycle count functionality.
    """
    cycle_count = models.ForeignKey(CycleCount, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    expected_quantity = models.IntegerField()
    counted_quantity = models.IntegerField(null=True, blank=True)
    discrepancy_notes = models.TextField(blank=True)
    actual_quantity = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cycle Count Item'
        verbose_name_plural = 'Cycle Count Items'

    def __str__(self):
        return f"{self.product} - Expected: {self.expected_quantity}, Counted: {self.counted_quantity}"

class VanInventory(models.Model):
    """
    Temporary model to maintain compatibility with existing views.
    This will be replaced with proper van inventory functionality.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Van Inventory'
        verbose_name_plural = 'Van Inventories'

    def __str__(self):
        return f"{self.product} - Qty: {self.quantity}"