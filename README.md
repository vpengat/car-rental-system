# 🚗 DriveNow — Car Rental System

A simple, clean car rental web application built with **Python + Flask + SQLite**.
Developed as a university Software Engineering project.

---

## 📁 Project Structure

```
car_rental_system/
├── app.py              ← Main Flask application
├── init_db.py          ← Database setup & seed script
├── database.db         ← SQLite database (created by init_db.py)
├── requirements.txt    ← Python dependencies
├── README.md
│
├── templates/          ← Jinja2 HTML templates
│   ├── base.html
│   ├── login.html
│   ├── customer_dashboard.html
│   ├── staff_dashboard.html
│   ├── search.html
│   ├── car_details.html
│   ├── booking.html
│   ├── reservations.html
│   ├── manage_vehicles.html
│   ├── add_vehicle.html
│   └── edit_vehicle.html
│
└── static/
    └── style.css       ← All styling
```

---

## ⚙️ Setup & Run

### 1. Prerequisites
- Python 3.8 or higher installed

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialise the database
```bash
python init_db.py
```
This creates `database.db` with sample cars and test users.

### 4. Start the application
```bash
python app.py
```

### 5. Open in your browser
```
http://127.0.0.1:5000
```

---

## 🔑 Test Credentials

| Role     | Username   | Password |
|----------|------------|----------|
| Customer | `customer` | `123`    |
| Staff    | `staff`    | `123`    |

---

## 🧭 Key Routes

| Route                    | Description                     |
|--------------------------|---------------------------------|
| `/`                      | Redirects to login or dashboard |
| `/login`                 | Login page                      |
| `/logout`                | Clears session                  |
| `/customer`              | Customer dashboard              |
| `/search`                | Browse available cars           |
| `/car/<id>`              | Car detail page                 |
| `/book/<id>`             | Booking form                    |
| `/reservations`          | Customer's booking history      |
| `/staff`                 | Staff dashboard with stats      |
| `/manage-vehicles`       | View & manage all vehicles      |
| `/add-vehicle`           | Add a new vehicle               |
| `/edit-vehicle/<id>`     | Edit an existing vehicle        |
| `/delete-vehicle/<id>`   | Delete a vehicle (POST)         |

---

## 🗄️ Database Schema

**users** — `id, username, password, role`  
**cars** — `id, model, category, price_per_day, availability, description`  
**reservations** — `id, user_id, car_id, pickup_date, dropoff_date`

---

## ✨ Features

- **Role-based access** — customers and staff see different interfaces
- **Car search** — filter by category (Sedan, SUV, Sports, Luxury, Electric…)
- **Booking logic** — cars become unavailable once booked
- **Staff CRUD** — add, edit, delete vehicles with instant feedback
- **Clean UI** — custom CSS with no external frameworks

---

## 🔄 Re-seed the Database

To reset everything and start fresh:
```bash
python init_db.py
```
> ⚠️ This drops all existing data.
