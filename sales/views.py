from django.views.generic import TemplateView, DetailView, CreateView, ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.db.models import Count, Q
from django.utils import timezone
from .models import Customer, Order, OrderItem

@login_required
def home(request):
    # Get basic sales statistics
    context = {
        'page_title': 'Sales Dashboard',
        'total_orders': Order.objects.count(),
        'total_customers': Customer.objects.count(),
        'recent_orders': Order.objects.order_by('-created_at')[:5],
        'recent_customers': Customer.objects.order_by('-created_at')[:5]
    }
    return render(request, 'sales/home.html', context)

class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'sales/customer/list.html'
    context_object_name = 'customers'
    ordering = ['name']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Customers'
        return context

class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer
    template_name = 'sales/customer/form.html'
    fields = ['name', 'contact_name', 'email', 'phone', 'address', 'route_day', 'route_sequence']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Add Customer'
        context['submit_text'] = 'Create Customer'
        return context

    def get_success_url(self):
        return reverse('sales:customer-detail', kwargs={'pk': self.object.pk})

class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer
    template_name = 'sales/customer/form.html'
    fields = ['name', 'contact_name', 'email', 'phone', 'address', 'route_day', 'route_sequence']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Edit Customer'
        context['submit_text'] = 'Update Customer'
        return context

    def get_success_url(self):
        return reverse('sales:customer-detail', kwargs={'pk': self.object.pk})

class CustomerDetailView(LoginRequiredMixin, DetailView):
    template_name = 'sales/customer/detail.html'
    model = Customer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.get_object()
        
        # Get order history
        context['recent_orders'] = Order.objects.filter(
            customer=customer
        ).order_by('-created_at')[:5]
        
        # Get favorite items (most ordered products)
        context['favorite_items'] = OrderItem.objects.filter(
            order__customer=customer
        ).values(
            'product__name',
            'product__id'
        ).annotate(
            order_count=Count('id')
        ).order_by('-order_count')[:10]
        
        # Get previous notes from orders
        context['previous_notes'] = Order.objects.filter(
            customer=customer,
            notes__isnull=False
        ).exclude(notes='').values_list('notes', flat=True)[:5]
        
        return context

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'sales/order/list.html'
    context_object_name = 'orders'
    ordering = ['-created_at']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Orders'
        return context

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'sales/order/detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Order #{self.object.pk}'
        return context

class OrderUpdateView(LoginRequiredMixin, UpdateView):
    model = Order
    template_name = 'sales/order/form.html'
    fields = ['status', 'department', 'po_number', 'approver_name', 'notes']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Edit Order #{self.object.pk}'
        context['submit_text'] = 'Update Order'
        return context

    def get_success_url(self):
        return reverse('sales:order-detail', kwargs={'pk': self.object.pk})

class OrderEntryView(LoginRequiredMixin, CreateView):
    template_name = 'sales/order/create.html'
    model = Order
    fields = ['department', 'po_number', 'approver_name', 'notes']
    
    def get_initial(self):
        initial = super().get_initial()
        self.customer = get_object_or_404(Customer, pk=self.kwargs['customer_pk'])
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customer'] = self.customer
        return context
    
    def form_valid(self, form):
        form.instance.customer = self.customer
        form.instance.created_by = self.request.user
        form.instance.status = 'draft'
        response = super().form_valid(form)
        
        # After saving, redirect to add items
        # Note: Order items handling will be added in a separate view
        return response
    
    def get_success_url(self):
        return reverse('sales:customer-detail', kwargs={'pk': self.customer.pk})

class RouteOverviewView(LoginRequiredMixin, TemplateView):
    template_name = 'sales/route/overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now()
        # Get today's route customers
        context['customers'] = Customer.objects.filter(
            route_day=today.strftime('%A')
        ).order_by('route_sequence')
        return context

class CustomerStopView(LoginRequiredMixin, DetailView):
    template_name = 'sales/route/customer_stop.html'
    model = Customer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.get_object()
        
        # Get next customer in route
        next_customer = Customer.objects.filter(
            route_day=timezone.now().strftime('%A'),
            route_sequence__gt=customer.route_sequence
        ).order_by('route_sequence').first()
        
        context['next_customer'] = next_customer
        context['google_maps_url'] = f"https://www.google.com/maps/search/?api=1&query={customer.address.replace(' ', '+')}"
        return context
