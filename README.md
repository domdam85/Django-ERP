# Business Management Application

A comprehensive web-based solution for managing warehouse, delivery, and sales operations for distribution companies. Built with Django and Bootstrap.

## Features

- Dashboard with key business metrics
- Sales Management
- Delivery Management
- Warehouse Operations
- Management Oversight
- Administrative Tools
- QuickBooks Desktop Integration

## Requirements

- Python 3.10+
- Django 5.0+
- Redis (for Celery tasks)
- QuickBooks Desktop with Web Connector

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

- `dashboard/`: Dashboard and metrics
- `sales/`: Sales management functionality
- `delivery/`: Delivery and route management
- `warehouse/`: Inventory and warehouse operations
- `management/`: Management tools and oversight
- `admin_tools/`: Administrative functionality
- `core/`: Shared functionality and settings

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
