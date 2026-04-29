# 🛒 SmashStrix – E-commerce Web Application

A full-featured e-commerce web application built using Django, featuring product management, offers, cart, checkout, wallet system, and secure cloud deployment.

## 🚀 Features

### 👤 User Side

* User registration & authentication
* Browse products with filters (category, brand, price, color)
* Product detail with zoom & image gallery
* Wishlist management
* Cart management with quantity control
* Coupon application system
* Checkout with address selection
* Wallet-based payments
* Order history & order tracking
* Product ratings & reviews
* Order cancellation & item-level cancellation
* Return request & refund to wallet

### 🛠 Admin Side

* Dashboard for managing:
  * Products
  * Categories
  * Brands
* Product image upload with cropping & resizing
* Color variant management with stock control
* Offer management (product & category level)
* Coupon management with validation rules
* Order management with status transitions
* Return approval/rejection system
* Wallet transaction tracking

## 🧠 Tech Stack

### Backend

* Django (Python)
* Django ORM

### Database

* PostgreSQL (Neon)

### Frontend

* HTML, CSS, TailwindCSS
* JavaScript

### Storage

* AWS S3 (media files)

### Deployment

* AWS EC2 (Ubuntu)
* Gunicorn (WSGI server)
* Nginx (reverse proxy)

## ⚙️ Installation (Local Setup)

### 1. Clone Repository

git clone https://github.com/Kiran-Raj-R/new_smashstrix.git

cd new_smashstrix

### 2. Create Virtual Environment

python -m venv venv

source venv/bin/activate   # Linux/Mac

venv\Scripts\activate      # Windows

### 3. Install Dependencies

pip install -r requirements.txt

### 4. Create `.env` File

SECRET_KEY=your_secret_key

DEBUG=True

DATABASE_URL=your_postgresql_url

AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_STORAGE_BUCKET_NAME=your_bucket
AWS_S3_REGION_NAME=your_region

### 5. Apply Migrations

python manage.py migrate

### 6. Create Superuser

python manage.py createsuperuser

### 7. Run Server

python manage.py runserver

## ☁️ Deployment Overview

Application is deployed using:

Nginx → Gunicorn → Django → PostgreSQL (Neon) → AWS S3

### Key Highlights

* Media files stored in AWS S3
* PostgreSQL used instead of SQLite
* Gunicorn handles application serving
* Nginx acts as reverse proxy
* HTTPS enabled using Certbot


## 🗂 Project Structure

smashstrix/

|── accounts/

│── adminpanel/

│── cart/

│── core/

│── coupons/

│── new_smashstrix/

│── products/

│── orders/

│── user/

│── wallet/

│── wishlist/

│── templates/

│── static/

│── manage.py

## 🧪 Key Functionalities Implemented

* Dynamic pricing with offers
* Coupon logic with min/max constraints
* Wallet refund system for cancellations/returns
* Image cropping & resizing (S3-compatible)
* Stock management via variants
* Rating system with verified purchase check

## 🔐 Security Features

* CSRF protection
* Secure authentication
* Environment variable management
* HTTPS enabled in production

## 📌 Future Improvements

* Payment gateway integration (Razorpay/Stripe)
* Redis caching
* Email notifications
* Advanced analytics dashboard

## 🙌 Acknowledgements

* Django Documentation
* AWS Documentation
* Neon PostgreSQL

## 📄 License

This project is for educational purposes.
