class DashboardManager {
    constructor() {
        this.charts = {};
        this.updateInterval = 60000; // 1 minute
        this.initializeEventListeners();
        this.initializeCharts();
        this.startPeriodicUpdates();
    }

    initializeEventListeners() {
        // Add click handlers for drill-down on metric cards
        document.querySelectorAll('.metric-card').forEach(card => {
            card.addEventListener('click', (e) => {
                if (!e.target.closest('a')) {  // Don't trigger if clicking the "View Details" link
                    this.handleMetricDrillDown(card.dataset.metricType);
                }
            });
        });

        // Time range selector for charts
        document.querySelectorAll('.btn-time-range').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.updateChartTimeRange(e.target.dataset.range);
                // Update active state
                document.querySelectorAll('.btn-time-range').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
            });
        });
    }

    initializeCharts() {
        const revenueCtx = document.getElementById('revenueChart').getContext('2d');
        this.charts.revenue = new Chart(revenueCtx, {
            type: 'line',
            data: window.revenue_chart_data || { labels: [], datasets: [] },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return '$' + context.raw.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }

    async handleMetricDrillDown(metricType) {
        try {
            const response = await fetch(`/management/api/metrics/detail/${metricType}/`);
            if (!response.ok) throw new Error('Failed to fetch metric details');
            const data = await response.json();
            this.showDrillDownModal(metricType, data);
        } catch (error) {
            console.error('Error fetching drill-down data:', error);
            this.showErrorNotification('Failed to load detailed metrics');
        }
    }

    showDrillDownModal(metricType, data) {
        const modalTitle = document.querySelector('#metricDetailModal .modal-title');
        const modalBody = document.querySelector('#metricDetailModal .modal-body');
        
        modalTitle.textContent = this.getMetricTitle(metricType);
        modalBody.innerHTML = this.formatDrillDownContent(metricType, data);
        
        const modal = new bootstrap.Modal(document.getElementById('metricDetailModal'));
        modal.show();
    }

    getMetricTitle(metricType) {
        const titles = {
            revenue: 'Revenue Details',
            orders: 'Order Analysis',
            customers: 'Customer Insights',
            inventory: 'Inventory Status'
        };
        return titles[metricType] || 'Metric Details';
    }

    formatDrillDownContent(metricType, data) {
        switch (metricType) {
            case 'revenue':
                return this.formatRevenueDetail(data);
            case 'orders':
                return this.formatOrdersDetail(data);
            case 'customers':
                return this.formatCustomersDetail(data);
            case 'inventory':
                return this.formatInventoryDetail(data);
            default:
                return '<p>No detailed data available</p>';
        }
    }

    formatRevenueDetail(data) {
        const categoryChart = this.createChartHTML('categoryChart', 'Revenue by Category');
        const customerChart = this.createChartHTML('customerChart', 'Top Customers');

        setTimeout(() => {
            this.initializeCategoryChart(data.revenue_by_category);
            this.initializeCustomerChart(data.top_customers);
        }, 0);

        return `
            <div class="row">
                <div class="col-md-6 mb-4">${categoryChart}</div>
                <div class="col-md-6 mb-4">${customerChart}</div>
            </div>
            <div class="text-muted mt-2">
                <small>Data period: ${data.period}</small>
            </div>
        `;
    }

    formatOrdersDetail(data) {
        const completionRate = (data.completed_orders / data.total_orders * 100).toFixed(1);
        
        return `
            <div class="row">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">Order Summary</h5>
                            <div class="d-flex justify-content-between mb-3">
                                <span>Total Orders:</span>
                                <strong>${data.total_orders}</strong>
                            </div>
                            <div class="d-flex justify-content-between mb-3">
                                <span>Completed:</span>
                                <strong>${data.completed_orders}</strong>
                            </div>
                            <div class="d-flex justify-content-between mb-3">
                                <span>Completion Rate:</span>
                                <strong>${completionRate}%</strong>
                            </div>
                            <div class="d-flex justify-content-between mb-3">
                                <span>Average Order Value:</span>
                                <strong>$${data.average_order_value.toFixed(2)}</strong>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">Orders by Status</h5>
                            <ul class="list-group list-group-flush">
                                ${data.orders_by_status.map(item => `
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        ${item.status}
                                        <span class="badge bg-primary rounded-pill">${item.count}</span>
                                    </li>
                                `).join('')}
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
            <div class="text-muted mt-2">
                <small>Data period: ${data.period}</small>
            </div>
        `;
    }

    formatCustomersDetail(data) {
        return `
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Customer Engagement</h5>
                    <div class="d-flex justify-content-between mb-3">
                        <span>Active Customers:</span>
                        <strong>${data.active_customers}</strong>
                    </div>
                    <div class="d-flex justify-content-between mb-3">
                        <span>New Customers (This Month):</span>
                        <strong>${data.new_customers}</strong>
                    </div>
                    <div class="d-flex justify-content-between mb-3">
                        <span>Average Orders per Customer:</span>
                        <strong>${data.average_orders_per_customer.toFixed(1)}</strong>
                    </div>
                    <div class="d-flex justify-content-between">
                        <span>Customer with Most Orders:</span>
                        <strong>${data.most_orders_by_customer} orders</strong>
                    </div>
                </div>
            </div>
            <div class="text-muted mt-2">
                <small>Data period: ${data.period}</small>
            </div>
        `;
    }

    formatInventoryDetail(data) {
        return `
            <div class="row">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">Inventory Summary</h5>
                            <div class="d-flex justify-content-between mb-3">
                                <span>Total Items in Stock:</span>
                                <strong>${data.total_items}</strong>
                            </div>
                            <div class="d-flex justify-content-between mb-3">
                                <span>Low Stock Items:</span>
                                <strong>${data.low_stock_items}</strong>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">Stock Value by Category</h5>
                            <ul class="list-group list-group-flush">
                                ${data.stock_by_category.map(item => `
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        ${item.category}
                                        <span class="badge bg-info rounded-pill">$${item.value.toLocaleString()}</span>
                                    </li>
                                `).join('')}
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
            <div class="mt-4">
                <h5>Recently Updated Inventory Items</h5>
                <ul class="list-group list-group-flush">
                    ${data.recent_updates.map(item => `
                        <li class="list-group-item">
                            ${item.name} - Quantity: ${item.quantity_on_hand}, Updated: ${new Date(item.last_updated).toLocaleDateString()}
                        </li>
                    `).join('')}
                </ul>
            </div>
        `;
    }

    updateChartTimeRange(range) {
        // Placeholder for updating chart data based on time range
        console.log(`Updating charts to time range: ${range}`);
    }

    updateCharts(revenueChartData) {
        if (this.charts.revenue) {
            this.charts.revenue.data = revenueChartData;
            this.charts.revenue.update();
        }
    }

    createChartHTML(chartId, title) {
        return `
            <div class="card">
                <div class="card-header">${title}</div>
                <div class="card-body">
                    <canvas id="${chartId}" height="300"></canvas>
                </div>
            </div>
        `;
    }

    initializeCategoryChart(categoryData) {
        const ctx = document.getElementById('categoryChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: categoryData.map(item => item.category),
                datasets: [{
                    label: 'Revenue',
                    data: categoryData.map(item => item.total),
                    backgroundColor: 'rgba(54, 162, 235, 0.8)',
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function (value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    initializeCustomerChart(customerData) {
        const ctx = document.getElementById('customerChart').getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: customerData.map(item => item.customer__name),
                datasets: [{
                    label: 'Revenue',
                    data: customerData.map(item => item.total),
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(255, 159, 64, 0.8)',
                        'rgba(255, 205, 86, 0.8)',
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(54, 162, 235, 0.8)'
                    ],
                }]
            },
            options: {
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    updateMetricCard(type, value, trend = null) {
        const card = document.querySelector(`[data-metric-type="${type}"]`);
        if (!card) return;

        const valueDisplay = card.querySelector('.metric-value');
        const trendDisplay = card.querySelector('.metric-trend');

        if (valueDisplay) {
            if (type === 'revenue' || type === 'inventory') {
                valueDisplay.textContent = `$${this.formatNumber(value)}`;
            } else {
                valueDisplay.textContent = this.formatNumber(value);
            }
        }

        if (trendDisplay && trend !== null) {
            const isPositive = trend > 0;
            trendDisplay.innerHTML = `
                <i class="fas fa-arrow-${isPositive ? 'up' : 'down'}"></i>
                ${Math.abs(trend).toFixed(1)}%
            `;
            trendDisplay.classList.remove('trend-up', 'trend-down');
            trendDisplay.classList.add(isPositive ? 'trend-up' : 'trend-down');
        }
    }

    updateProgressBar(id, value) {
        const progressBar = document.querySelector(`#${id} .progress-bar`);
        const label = document.querySelector(`#${id} .progress-label`);
        
        if (progressBar) {
            progressBar.style.width = `${value}%`;
            progressBar.setAttribute('aria-valuenow', value);

            // Update color based on value
            progressBar.className = 'progress-bar';
            if (value >= 90) {
                progressBar.classList.add('bg-success');
            } else if (value >= 70) {
                progressBar.classList.add('bg-info');
            } else if (value >= 50) {
                progressBar.classList.add('bg-warning');
            } else {
                progressBar.classList.add('bg-danger');
            }
        }
        
        if (label) {
            label.textContent = `${value.toFixed(1)}%`;
        }
    }

    formatNumber(value) {
        return value.toLocaleString(undefined, { maximumFractionDigits: 2 });
    }

    updateDashboardMetrics() {
        fetch('/management/api/dashboard_metrics/')
            .then(response => response.json())
            .then(data => {
                this.updateMetricCard('revenue', data.total_revenue, data.revenue_trend);
                this.updateMetricCard('orders', data.orders_completed);
                this.updateMetricCard('customers', data.active_customers, data.new_customers);
                this.updateMetricCard('inventory', data.total_inventory_value, data.low_stock_items);
                this.updateProgressBar('fulfillmentRate', data.fulfillment_rate);
                this.updateProgressBar('deliveryRate', data.delivery_rate);
                this.updateProgressBar('satisfactionRate', data.satisfaction_rate);
                this.updateProgressBar('inventoryAccuracy', data.inventory_accuracy);
                this.updateCharts(data.revenue_chart_data); // Update revenue chart
            })
            .catch(error => {
                console.error('Error fetching dashboard metrics:', error);
            });
    }

    showErrorNotification(message) {
        console.error(message);
    }

    startPeriodicUpdates() {
        this.updateDashboardMetrics();
        setInterval(() => this.updateDashboardMetrics(), this.updateInterval);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.dashboardManager = new DashboardManager();
});
