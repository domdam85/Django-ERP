from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import (
    Product, Vendor, PurchaseOrder, POItem, ReceiptLog, ReceiptItem,
    AggregatedPickList, PickListItem, StagingArea, StagedOrder, CycleCount,
    CycleCountItem
)

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'sku', 'description', 'unit_price', 'reorder_point', 'location']

class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['vendor', 'po_number', 'order_date', 'expected_date', 'notes']
        widgets = {
            'order_date': forms.DateInput(attrs={'type': 'date'}),
            'expected_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_expected_date(self):
        expected_date = self.cleaned_data.get('expected_date')
        order_date = self.cleaned_data.get('order_date')
        
        if expected_date and order_date and expected_date < order_date:
            raise ValidationError("Expected date cannot be earlier than order date")
        
        return expected_date

POItemFormSet = inlineformset_factory(
    PurchaseOrder,
    POItem,
    fields=('product', 'ordered_quantity', 'unit_price', 'notes'),
    extra=1,
    can_delete=True
)

class ReceiveItemForm(forms.Form):
    notes = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        po = kwargs.get('initial', {}).get('po')
        
        if po:
            # Add dynamic fields for each PO item
            for item in po.items.all():
                remaining = item.ordered_quantity - item.received_quantity
                if remaining > 0:
                    self.fields[f'received_items_{item.id}'] = forms.IntegerField(
                        min_value=0,
                        max_value=remaining,
                        required=False,
                        widget=forms.NumberInput(attrs={
                            'class': 'form-control',
                            'data-item-id': item.id
                        })
                    )
                    self.fields[f'notes_{item.id}'] = forms.CharField(
                        required=False,
                        widget=forms.Textarea(attrs={'rows': 2})
                    )

    def clean(self):
        cleaned_data = super().clean()
        received_items = {}

        # Extract received quantities
        for field_name, value in cleaned_data.items():
            if field_name.startswith('received_items_') and value:
                item_id = field_name.split('_')[-1]
                received_items[item_id] = value
                # Add any notes for this item
                notes_field = f'notes_{item_id}'
                if notes_field in cleaned_data:
                    cleaned_data[notes_field] = cleaned_data[notes_field]

        cleaned_data['received_items'] = received_items
        return cleaned_data

class PickListForm(forms.ModelForm):
    class Meta:
        model = AggregatedPickList
        fields = ['delivery_route', 'delivery_date', 'notes']
        widgets = {
            'delivery_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_delivery_date(self):
        delivery_date = self.cleaned_data.get('delivery_date')
        if delivery_date < timezone.now().date():
            raise ValidationError("Delivery date cannot be in the past")
        return delivery_date

class PickItemForm(forms.Form):
    quantity = forms.IntegerField(min_value=0)
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}))

    def __init__(self, *args, **kwargs):
        max_quantity = kwargs.pop('max_quantity', None)
        super().__init__(*args, **kwargs)
        if max_quantity is not None:
            self.fields['quantity'].max_value = max_quantity

class StageOrderForm(forms.ModelForm):
    class Meta:
        model = StagedOrder
        fields = ['staging_area', 'notes']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active staging areas
        self.fields['staging_area'].queryset = StagingArea.objects.filter(status='active')

class CycleCountForm(forms.ModelForm):
    class Meta:
        model = CycleCount
        fields = ['zone', 'notes']

class CycleCountItemForm(forms.ModelForm):
    class Meta:
        model = CycleCountItem
        fields = ['counted_quantity', 'discrepancy_notes']

    def __init__(self, *args, **kwargs):
        expected_quantity = kwargs.pop('expected_quantity', None)
        super().__init__(*args, **kwargs)
        if expected_quantity is not None:
            self.initial['expected_quantity'] = expected_quantity
            self.fields['counted_quantity'].widget.attrs['placeholder'] = f"Expected: {expected_quantity}"

    def clean(self):
        cleaned_data = super().clean()
        counted_quantity = cleaned_data.get('counted_quantity')
        expected_quantity = self.initial.get('expected_quantity')

        if counted_quantity != expected_quantity and not cleaned_data.get('discrepancy_notes'):
            raise ValidationError({
                'discrepancy_notes': "Please provide notes explaining the discrepancy"
            })
