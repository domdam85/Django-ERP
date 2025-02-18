from django.views.generic import TemplateView, DetailView, CreateView, UpdateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Delivery, DeliveryException, VanLoadingRecord
from management.models import Route, CustomerStop

@login_required
def home(request):
    today = timezone.now()
    context = {
        'active_deliveries': Delivery.objects.filter(
            route__delivery_driver=request.user,
            status__in=['pending', 'in_progress'],
            created_at__date=today.date()
        ),
        'completed_deliveries': Delivery.objects.filter(
            route__delivery_driver=request.user,
            status='completed',
            created_at__date=today.date()
        ),
        'exceptions': DeliveryException.objects.filter(
            delivery__route__delivery_driver=request.user,
            reported_at__date=today.date()
        )
    }
    return render(request, 'delivery/home.html', context)

class RouteListView(LoginRequiredMixin, ListView):
    model = Route
    template_name = 'delivery/route/list.html'
    context_object_name = 'routes'

    def get_queryset(self):
        return Route.objects.filter(
            delivery_driver=self.request.user,
            day=timezone.now().strftime('%A')
        ).order_by('start_time')

class RouteDetailView(LoginRequiredMixin, DetailView):
    model = Route
    template_name = 'delivery/route/detail.html'
    context_object_name = 'route'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Route Details - {self.object.name}'
        context['stops'] = self.object.stops.all().order_by('sequence')
        context['total_stops'] = context['stops'].count()
        context['completed_stops'] = context['stops'].filter(status='completed').count()
        return context

class RouteOverviewView(LoginRequiredMixin, TemplateView):
    template_name = 'delivery/route/overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now()

        # Get today's route assigned to the delivery driver
        route = Route.objects.filter(
            delivery_driver=self.request.user,
            day=today.strftime('%A')
        ).first()

        if route:
            # Get all deliveries for this route
            context['stops'] = CustomerStop.objects.filter(
                route=route
            ).select_related('customer').prefetch_related('customer__orders__delivery')

            # Get van loading status
            context['van_loading'] = VanLoadingRecord.objects.filter(
                route=route
            ).first()

        context['route'] = route
        return context

class NextStopView(LoginRequiredMixin, DetailView):
    template_name = 'delivery/route/next_stop.html'
    model = CustomerStop

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stop = self.get_object()
        
        # Get deliveries for this stop
        context['deliveries'] = Delivery.objects.filter(
            stop=stop,
            status__in=['pending', 'in_transit']
        ).select_related('order')
        
        # Get next stop
        context['next_stop'] = CustomerStop.objects.filter(
            route=stop.route,
            sequence__gt=stop.sequence
        ).first()
        
        # Generate Google Maps URL
        context['google_maps_url'] = f"https://www.google.com/maps/search/?api=1&query={stop.customer.address.replace(' ', '+')}"
        
        return context

class DeliveryVerificationView(LoginRequiredMixin, UpdateView):
    template_name = 'delivery/delivery/verify.html'
    model = Delivery
    fields = ['status', 'notes']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        delivery = self.get_object()
        context['order_items'] = delivery.order.items.all()
        return context

    def form_valid(self, form):
        if form.cleaned_data['status'] == 'delivered':
            form.instance.delivered_at = timezone.now()
        return super().form_valid(form)

    def get_success_url(self):
        delivery = self.get_object()
        return reverse('delivery:next-stop', kwargs={'pk': delivery.stop.pk})

class ProofOfDeliveryView(LoginRequiredMixin, UpdateView):
    template_name = 'delivery/delivery/proof.html'
    model = Delivery
    fields = ['proof_of_delivery', 'signature', 'notes']

    def form_valid(self, form):
        form.instance.status = 'delivered'
        form.instance.delivered_at = timezone.now()
        return super().form_valid(form)

    def get_success_url(self):
        delivery = self.get_object()
        next_stop = CustomerStop.objects.filter(
            route=delivery.route,
            sequence__gt=delivery.stop.sequence
        ).first()
        if next_stop:
            return reverse('delivery:next-stop', kwargs={'pk': next_stop.pk})
        return reverse('delivery:route-overview')

class DeliveryExceptionView(LoginRequiredMixin, CreateView):
    template_name = 'delivery/delivery/exception.html'
    model = DeliveryException
    fields = ['exception_type', 'description']

    def form_valid(self, form):
        delivery = get_object_or_404(Delivery, pk=self.kwargs['delivery_pk'])
        form.instance.delivery = delivery
        form.instance.reported_by = self.request.user
        delivery.status = 'failed'
        delivery.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('delivery:next-stop', kwargs={'pk': self.kwargs['stop_pk']})

class VanLoadingView(LoginRequiredMixin, UpdateView):
    template_name = 'delivery/van/loading.html'
    model = VanLoadingRecord
    fields = ['status', 'notes']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['deliveries'] = Delivery.objects.filter(
            route=self.object.route,
            status='pending'
        ).select_related('order', 'stop')
        return context

    def form_valid(self, form):
        if form.cleaned_data['status'] == 'completed':
            form.instance.completed_at = timezone.now()
        elif form.cleaned_data['status'] == 'in_progress' and not form.instance.started_at:
            form.instance.started_at = timezone.now()
        return super().form_valid(form)

    def get_success_url(self):
        if self.object.status == 'completed':
            return reverse('delivery:route-overview')
        return reverse('delivery:van-loading', kwargs={'pk': self.object.pk})

class DeliveryListView(LoginRequiredMixin, ListView):
    model = Delivery
    template_name = 'delivery/delivery/list.html'
    context_object_name = 'deliveries'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Deliveries'
        return context

class DeliveryDetailView(LoginRequiredMixin, DetailView):
    model = Delivery
    template_name = 'delivery/delivery/detail.html'
    context_object_name = 'delivery'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Delivery #{self.object.id}'
        return context

class DeliveryUpdateView(LoginRequiredMixin, UpdateView):
    model = Delivery
    template_name = 'delivery/delivery/form.html'
    fields = ['status', 'notes']
    success_url = reverse_lazy('delivery:delivery-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Update Delivery #{self.object.id}'
        return context

class DeliveryVerificationView(LoginRequiredMixin, UpdateView):
    model = Delivery
    template_name = 'delivery/delivery/verify.html'
    fields = ['status', 'notes']
    context_object_name = 'delivery'

    def get_success_url(self):
        return reverse_lazy('delivery:next-stop', kwargs={'pk': self.object.stop.pk})

class ProofOfDeliveryView(LoginRequiredMixin, UpdateView):
    model = Delivery
    template_name = 'delivery/delivery/proof.html'
    fields = ['proof_of_delivery', 'signature', 'notes']
    context_object_name = 'delivery'

    def get_success_url(self):
        return reverse_lazy('delivery:next-stop', kwargs={'pk': self.object.stop.pk})

class DeliveryExceptionView(LoginRequiredMixin, UpdateView):
    model = Delivery
    template_name = 'delivery/delivery/exception.html'
    fields = ['exception_type', 'description']
    context_object_name = 'delivery'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stop'] = get_object_or_404(CustomerStop, pk=self.kwargs['stop_pk'])
        return context

    def get_success_url(self):
        return reverse_lazy('delivery:next-stop', kwargs={'pk': self.kwargs['stop_pk']})
