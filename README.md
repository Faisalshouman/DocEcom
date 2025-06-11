# DocEcom – PDF E-Commerce Backend

DocEcom is a backend project built to sell downloadable PDF documents. After a successful purchase, customers receive access to download the files securely.

## Features

- Product catalog with PDF support
- Order and payment system (e.g., PayPal or Stripe integration)
- Secure download links for buyers
- Admin panel for product management

## Technologies Used

- Python (Django or Flask)
- PostgreSQL or SQLite
- Django REST Framework (if applicable)
- PayPal SDK / Stripe (optional)

## Getting Started

1. **Clone the Repository**
```bash
git clone https://github.com/Faisalshouman/DocEcom.git
cd DocEcom

Install Dependencies

```bash
pip install -r requirements.txt

Run Migrations

```bash
python manage.py migrate

Start the Development Server

```bash
python manage.py runserver

Access Admin Panel

```bash
python manage.py createsuperuser

Visit http://localhost:8000/admin to manage products and orders.

