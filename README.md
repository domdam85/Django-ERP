# Business Management Application

A comprehensive web-based (Django+Bootstrap+HTMX) solution for managing warehouse, delivery, and sales operations for distribution companies. Built with Django and Bootstrap.

## Features

- Overdashboard with current business operations summarized
- Sales Route module
- Delivery Route module
- Warehouse Operations module
- Management Oversight Desktop Interface
- Administrative Tools
- QuickBooks Desktop Integration via the Conductor Python SDK

## Requirements

- Python 3.10+
- Django 5.0+
- Conductor Python SDK 1.0+ (PyPi/pip: conductor-py)

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Update the variables in `.env`

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Project Structure

- `sales/`: Sales management functionality
- `delivery/`: Delivery and route management
- `warehouse/`: Inventory and warehouse operations
- `management/`: Management tools and oversight
- `admin-tools/`: Administrative functionality - reskinned to match application theme and integrated into navigation
- `core/`: Shared functionality and settings
