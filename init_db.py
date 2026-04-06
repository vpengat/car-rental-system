import sqlite3

DATABASE = 'database.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Create tables
    c.executescript('''
        DROP TABLE IF EXISTS reservations;
        DROP TABLE IF EXISTS cars;
        DROP TABLE IF EXISTS users;

        CREATE TABLE users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role     TEXT NOT NULL CHECK(role IN ('customer','staff'))
        );

        CREATE TABLE cars (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            model         TEXT NOT NULL,
            category      TEXT NOT NULL,
            price_per_day REAL NOT NULL,
            availability  INTEGER NOT NULL DEFAULT 1,
            description   TEXT
        );

        CREATE TABLE reservations (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            car_id       INTEGER NOT NULL,
            pickup_date  TEXT NOT NULL,
            dropoff_date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (car_id)  REFERENCES cars(id)
        );
    ''')

    # Seed users
    c.executemany(
        'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
        [
            ('customer', '123', 'customer'),
            ('staff',    '123', 'staff'),
            ('alice',    'alice123', 'customer'),
        ]
    )

    # Seed cars
    cars = [
        ('Toyota Corolla',      'Sedan',   45.00, 1, 'Reliable and fuel-efficient sedan. Perfect for city driving and long road trips.'),
        ('Honda Civic',         'Sedan',   48.00, 1, 'Sporty and comfortable sedan with excellent fuel economy and modern features.'),
        ('Ford Mustang',        'Sports',  95.00, 1, 'Iconic American muscle car. Thrilling V8 performance with head-turning style.'),
        ('BMW 3 Series',        'Luxury',  120.00,1, 'Premium luxury sedan with cutting-edge technology and superb driving dynamics.'),
        ('Toyota RAV4',         'SUV',     70.00, 1, 'Versatile SUV with all-wheel drive. Great for families and outdoor adventures.'),
        ('Ford Explorer',       'SUV',     80.00, 1, 'Spacious 7-seat SUV with powerful engine. Ideal for large families or groups.'),
        ('Mercedes-Benz C-Class','Luxury', 135.00,1, 'Sophisticated luxury sedan with premium interior and advanced safety systems.'),
        ('Chevrolet Camaro',    'Sports',  90.00, 1, 'Bold and powerful sports car with aggressive styling and high-performance engine.'),
        ('Hyundai Elantra',     'Sedan',   40.00, 1, 'Affordable and practical sedan with modern infotainment and great warranty.'),
        ('Jeep Wrangler',       'SUV',     85.00, 1, 'The ultimate off-road vehicle. Go anywhere, anytime with confidence.'),
        ('Tesla Model 3',       'Electric',110.00,1, 'All-electric sedan with incredible range, Autopilot, and over-the-air updates.'),
        ('Volkswagen Golf',     'Hatchback',52.00,1, 'Fun-to-drive hatchback with excellent build quality and practical cargo space.'),
    ]
    c.executemany(
        'INSERT INTO cars (model, category, price_per_day, availability, description) VALUES (?, ?, ?, ?, ?)',
        cars
    )

    conn.commit()
    conn.close()
    print("✅  Database initialised with sample users and cars.")
    print()
    print("   Test credentials:")
    print("   ┌──────────────┬──────────┬──────────┐")
    print("   │ Role         │ Username │ Password │")
    print("   ├──────────────┼──────────┼──────────┤")
    print("   │ Customer     │ customer │ 123      │")
    print("   │ Staff        │ staff    │ 123      │")
    print("   └──────────────┴──────────┴──────────┘")


if __name__ == '__main__':
    init_db()
