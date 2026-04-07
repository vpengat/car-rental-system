from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'car_rental_secret_key_2024'
DATABASE = 'database.db'


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ──────────────────────────────────────────────
# AUTH ROUTES
# ──────────────────────────────────────────────

@app.route('/')
def index():
    if 'user_id' in session:
        if session['role'] == 'staff':
            return redirect(url_for('staff_dashboard'))
        return redirect(url_for('customer_dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE username = ? AND password = ?',
            (username, password)
        ).fetchone()
        db.close()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            if user['role'] == 'staff':
                return redirect(url_for('staff_dashboard'))
            return redirect(url_for('customer_dashboard'))
        flash('Invalid username or password.', 'error')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ──────────────────────────────────────────────
# CUSTOMER ROUTES
# ──────────────────────────────────────────────

@app.route('/customer')
def customer_dashboard():
    if 'user_id' not in session or session['role'] != 'customer':
        return redirect(url_for('login'))
    db = get_db()
    featured = db.execute(
        'SELECT * FROM cars WHERE availability = 1 LIMIT 6'
    ).fetchall()
    categories = db.execute(
        'SELECT DISTINCT category FROM cars'
    ).fetchall()
    db.close()
    return render_template('customer_dashboard.html', cars=featured, categories=categories)


@app.route('/search')
def search():
    if 'user_id' not in session or session['role'] != 'customer':
        return redirect(url_for('login'))
    category = request.args.get('category', '')
    db = get_db()
    if category:
        cars = db.execute(
            'SELECT * FROM cars WHERE category = ? AND availability = 1',
            (category,)
        ).fetchall()
    else:
        cars = db.execute(
            'SELECT * FROM cars WHERE availability = 1'
        ).fetchall()
    categories = db.execute('SELECT DISTINCT category FROM cars').fetchall()
    db.close()
    return render_template('search.html', cars=cars, categories=categories, selected=category)


@app.route('/car/<int:car_id>')
def car_details(car_id):
    if 'user_id' not in session or session['role'] != 'customer':
        return redirect(url_for('login'))
    db = get_db()
    car = db.execute('SELECT * FROM cars WHERE id = ?', (car_id,)).fetchone()
    db.close()
    if not car:
        flash('Car not found.', 'error')
        return redirect(url_for('search'))
    return render_template('car_details.html', car=car)


@app.route('/book/<int:car_id>', methods=['GET', 'POST'])
def book_car(car_id):
    if 'user_id' not in session or session['role'] != 'customer':
        return redirect(url_for('login'))

    db = get_db()
    car = db.execute('SELECT * FROM cars WHERE id = ?', (car_id,)).fetchone()

    if not car:
        db.close()
        flash('Car not found.', 'error')
        return redirect(url_for('search'))

    if request.method == 'POST':
        pickup = request.form['pickup_date']
        dropoff = request.form['dropoff_date']

        if pickup >= dropoff:
            flash('Drop-off date must be after pickup date.', 'error')
        else:
            conflict = db.execute(
                '''
                SELECT * FROM reservations
                WHERE car_id = ?
                AND pickup_date < ?
                AND dropoff_date > ?
                ''',
                (car_id, dropoff, pickup)
            ).fetchone()

            if conflict:
                flash('This car is already booked for the selected dates.', 'error')
            elif car['availability'] == 0:
                flash('This car is not available for booking.', 'error')
            else:
                db.execute(
                    'INSERT INTO reservations (user_id, car_id, pickup_date, dropoff_date) VALUES (?, ?, ?, ?)',
                    (session['user_id'], car_id, pickup, dropoff)
                )
                db.execute('UPDATE cars SET availability = 0 WHERE id = ?', (car_id,))
                db.commit()
                db.close()
                flash('Booking confirmed! Enjoy your ride.', 'success')
                return redirect(url_for('reservations'))

    db.close()
    return render_template('booking.html', car=car)


@app.route('/reservations')
def reservations():
    if 'user_id' not in session or session['role'] != 'customer':
        return redirect(url_for('login'))
    db = get_db()
    rows = db.execute(
        '''SELECT r.id, r.car_id, r.pickup_date, r.dropoff_date,
                  c.model, c.category, c.price_per_day
           FROM reservations r
           JOIN cars c ON r.car_id = c.id
           WHERE r.user_id = ?
           ORDER BY r.id DESC''',
        (session['user_id'],)
    ).fetchall()
    db.close()
    return render_template('reservations.html', reservations=rows)


@app.route('/cancel-reservation/<int:reservation_id>', methods=['POST'])
def cancel_reservation(reservation_id):
    if 'user_id' not in session or session['role'] != 'customer':
        return redirect(url_for('login'))

    db = get_db()

    reservation = db.execute(
        '''SELECT * FROM reservations
           WHERE id = ? AND user_id = ?''',
        (reservation_id, session['user_id'])
    ).fetchone()

    if not reservation:
        db.close()
        flash('Reservation not found.', 'error')
        return redirect(url_for('reservations'))

    car_id = reservation['car_id']

    db.execute('DELETE FROM reservations WHERE id = ?', (reservation_id,))

    remaining = db.execute(
        'SELECT * FROM reservations WHERE car_id = ?',
        (car_id,)
    ).fetchone()

    if not remaining:
        db.execute('UPDATE cars SET availability = 1 WHERE id = ?', (car_id,))

    db.commit()
    db.close()

    flash('Reservation cancelled successfully.', 'success')
    return redirect(url_for('reservations'))


# ──────────────────────────────────────────────
# STAFF ROUTES
# ──────────────────────────────────────────────

@app.route('/staff')
def staff_dashboard():
    if 'user_id' not in session or session['role'] != 'staff':
        return redirect(url_for('login'))
    db = get_db()
    total_cars = db.execute('SELECT COUNT(*) FROM cars').fetchone()[0]
    available = db.execute('SELECT COUNT(*) FROM cars WHERE availability = 1').fetchone()[0]
    total_bookings = db.execute('SELECT COUNT(*) FROM reservations').fetchone()[0]
    db.close()
    return render_template(
        'staff_dashboard.html',
        total_cars=total_cars,
        available=available,
        total_bookings=total_bookings
    )


@app.route('/staff-reservations')
def staff_reservations():
    if 'user_id' not in session or session['role'] != 'staff':
        return redirect(url_for('login'))

    db = get_db()
    rows = db.execute(
        '''SELECT r.id, r.pickup_date, r.dropoff_date,
                  u.username,
                  c.model, c.category, c.price_per_day
           FROM reservations r
           JOIN users u ON r.user_id = u.id
           JOIN cars c ON r.car_id = c.id
           ORDER BY r.id DESC'''
    ).fetchall()
    db.close()

    return render_template('staff_reservations.html', reservations=rows)


@app.route('/manage-vehicles')
def manage_vehicles():
    if 'user_id' not in session or session['role'] != 'staff':
        return redirect(url_for('login'))
    db = get_db()
    cars = db.execute('SELECT * FROM cars ORDER BY id DESC').fetchall()
    db.close()
    return render_template('manage_vehicles.html', cars=cars)


@app.route('/add-vehicle', methods=['GET', 'POST'])
def add_vehicle():
    if 'user_id' not in session or session['role'] != 'staff':
        return redirect(url_for('login'))
    if request.method == 'POST':
        model = request.form['model']
        category = request.form['category']
        price = request.form['price_per_day']
        availability = 1 if request.form.get('availability') else 0
        description = request.form['description']
        db = get_db()
        db.execute(
            'INSERT INTO cars (model, category, price_per_day, availability, description) VALUES (?, ?, ?, ?, ?)',
            (model, category, price, availability, description)
        )
        db.commit()
        db.close()
        flash(f'"{model}" has been added successfully.', 'success')
        return redirect(url_for('manage_vehicles'))
    return render_template('add_vehicle.html')


@app.route('/edit-vehicle/<int:car_id>', methods=['GET', 'POST'])
def edit_vehicle(car_id):
    if 'user_id' not in session or session['role'] != 'staff':
        return redirect(url_for('login'))
    db = get_db()
    car = db.execute('SELECT * FROM cars WHERE id = ?', (car_id,)).fetchone()
    if not car:
        flash('Vehicle not found.', 'error')
        db.close()
        return redirect(url_for('manage_vehicles'))

    if request.method == 'POST':
        model = request.form['model']
        category = request.form['category']
        price = request.form['price_per_day']
        availability = 1 if request.form.get('availability') else 0
        description = request.form['description']
        db.execute(
            'UPDATE cars SET model=?, category=?, price_per_day=?, availability=?, description=? WHERE id=?',
            (model, category, price, availability, description, car_id)
        )
        db.commit()
        db.close()
        flash(f'"{model}" updated successfully.', 'success')
        return redirect(url_for('manage_vehicles'))

    db.close()
    return render_template('edit_vehicle.html', car=car)


@app.route('/delete-vehicle/<int:car_id>', methods=['POST'])
def delete_vehicle(car_id):
    if 'user_id' not in session or session['role'] != 'staff':
        return redirect(url_for('login'))
    db = get_db()
    car = db.execute('SELECT model FROM cars WHERE id = ?', (car_id,)).fetchone()
    if car:
        db.execute('DELETE FROM cars WHERE id = ?', (car_id,))
        db.execute('DELETE FROM reservations WHERE car_id = ?', (car_id,))
        db.commit()
        flash(f'"{car["model"]}" deleted successfully.', 'success')
    db.close()
    return redirect(url_for('manage_vehicles'))


if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        print("Database not found. Run 'python init_db.py' first.")
    app.run(debug=True)