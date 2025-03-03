# Generated by Django 5.1.6 on 2025-02-17 20:10

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sales', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Goal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('goal_type', models.CharField(choices=[('sales', 'Sales Target'), ('delivery', 'Delivery Target'), ('inventory', 'Inventory Target')], max_length=20)),
                ('target_value', models.DecimalField(decimal_places=2, max_digits=10)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('progress', models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='goals', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-end_date'],
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], default='medium', max_length=10)),
                ('read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('report_type', models.CharField(choices=[('daily', 'Daily Report'), ('weekly', 'Weekly Report'), ('monthly', 'Monthly Report'), ('custom', 'Custom Report')], max_length=20)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('content', models.JSONField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('generated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('day', models.CharField(max_length=20)),
                ('territory', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[('planning', 'Planning'), ('assigned', 'Assigned'), ('in_progress', 'In Progress'), ('completed', 'Completed')], max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('qb_list_id', models.CharField(blank=True, max_length=50)),
                ('delivery_driver', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='delivery_routes', to=settings.AUTH_USER_MODEL)),
                ('sales_rep', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sales_routes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['day', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('due_date', models.DateTimeField()),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], default='medium', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('assigned_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_tasks', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-due_date'],
            },
        ),
        migrations.CreateModel(
            name='PerformanceMetric',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('metric_type', models.CharField(choices=[('sales', 'Sales Performance'), ('delivery', 'Delivery Performance'), ('warehouse', 'Warehouse Performance')], max_length=20)),
                ('date', models.DateField()),
                ('value', models.DecimalField(decimal_places=2, max_digits=10)),
                ('target', models.DecimalField(decimal_places=2, max_digits=10)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='performance_metrics', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date'],
                'unique_together': {('user', 'metric_type', 'date')},
            },
        ),
        migrations.CreateModel(
            name='CustomerStop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sequence', models.PositiveIntegerField()),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sales.customer')),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stops', to='management.route')),
            ],
            options={
                'ordering': ['route', 'sequence'],
                'unique_together': {('route', 'sequence')},
            },
        ),
    ]
